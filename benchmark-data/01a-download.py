import logging
import warnings
from collections import defaultdict
from multiprocessing import get_context
from typing import Tuple

import click
import qcelemental
from openeye import oechem
from openff.qcsubmit.results import OptimizationResultCollection
from openff.qcsubmit.results.filters import (
    CMILESResultFilter,
    ConnectivityFilter,
    RecordStatusFilter,
    SMILESFilter,
)
from openff.toolkit.topology import Molecule
from openff.toolkit.topology.molecule import SmilesParsingError
from openff.toolkit.typing.engines.smirnoff import ForceField
from openff.toolkit.utils import (
    GLOBAL_TOOLKIT_REGISTRY,
    OpenEyeToolkitWrapper,
    UndefinedStereochemistryError,
)
from qcportal import FractalClient
from qcportal.models.records import RecordStatusEnum
from tqdm import tqdm

N_PROCESSES = 8


class InvalidCMILESFilter(CMILESResultFilter):
    def _filter_function(self, result) -> bool:

        try:
            Molecule.from_mapped_smiles(result.cmiles, allow_undefined_stereo=True)
        except (ValueError, SmilesParsingError):
            return False

        return True


def _can_parameterize(smiles: str) -> Tuple[str, bool]:

    try:

        for toolkit in GLOBAL_TOOLKIT_REGISTRY.registered_toolkits:

            if isinstance(toolkit, OpenEyeToolkitWrapper):
                continue

            GLOBAL_TOOLKIT_REGISTRY.deregister_toolkit(toolkit)

        molecule = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
        force_field = ForceField("openff-2.0.0.offxml")

        force_field.create_openmm_system(molecule.to_topology())

    except:
        return smiles, False

    return smiles, True


def _process_molecule(record_and_molecule) -> oechem.OEMol:
    """Convert a QC record and its associated molecule into an OE molecule which
    has been tagged with the associated SMILES, final energy and record id."""

    record, molecule = record_and_molecule

    oe_molecule = molecule.to_openeye()
    oechem.OE3DToInternalStereo(oe_molecule)

    final_energy = record.get_final_energy() * qcelemental.constants.hartree2kcalmol

    # add name and energy tag to the mol
    oechem.OESetSDData(oe_molecule, "SMILES QCArchive", molecule.to_smiles())
    oechem.OESetSDData(oe_molecule, "Energy QCArchive", str(final_energy))
    oechem.OESetSDData(oe_molecule, "Record QCArchive", str(record.id))

    return oe_molecule


@click.command()
@click.argument(
    "data_set",
    nargs=1,
    type=click.STRING,
)
def main(data_set):
    """Process and store optimized QC geometries from a QCArchive dataset.

    The DATA_SET should likely be one of:

    \b
    * "OpenFF Full Optimization Benchmark 1"
    * "OpenFF Industry Benchmark Season 1 v1.0"

    The processed molecules tagged with information from the QC record, including the
    CMILES and QC energy, will be stored in a new `01-processed-qm.sdf` file and
    additionally information about the included records will be stored in
    `01-processed-qm.json`.
    """

    warnings.filterwarnings("ignore")
    logging.getLogger("openff.toolkit").setLevel(logging.ERROR)

    # Make sure we consistently only use OE in this script

    print("1a) Parsing collection")

    client = FractalClient()

    result_collection = OptimizationResultCollection.from_server(
        client=client,
        datasets=data_set,
        spec_name="default",
    )

    # save the energy result collection to a JSON file
    with open("industry-benchmark-set-result-collection-downloaded.json", "w") as file:
        file.write(result_collection.json())

if __name__ == "__main__":
    main()
