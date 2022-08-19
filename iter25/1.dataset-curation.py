import copy
import functools
import json
import logging
import random
from collections import defaultdict
from multiprocessing import Pool
from tempfile import NamedTemporaryFile

from openff.qcsubmit.results import (OptimizationResultCollection,
                                     TorsionDriveResultCollection)
from openff.qcsubmit.results.filters import (ConformerRMSDFilter,
                                             ConnectivityFilter, ElementFilter,
                                             HydrogenBondFilter,
                                             RecordStatusFilter,
                                             ResultRecordFilter, SMARTSFilter,
                                             SMILESFilter)
from openff.toolkit.topology import Topology
from openff.toolkit.typing.engines.smirnoff import ForceField
from openff.toolkit.utils import UndefinedStereochemistryError
from qcportal import FractalClient
from qcportal.models import TorsionDriveRecord
from qcportal.models.records import RecordStatusEnum
from tqdm import tqdm


class UndefinedStereoFilter(ResultRecordFilter):
    def _filter_function(self, result, record, molecule) -> bool:

        has_stereochemistry = True

        molecule = copy.deepcopy(molecule)
        molecule._conformers = [molecule.conformers[0]]

        try:

            with NamedTemporaryFile(suffix=".sdf") as file:
                molecule.to_file(file.name, "SDF")
                molecule.from_file(file.name)

        except UndefinedStereochemistryError:
            has_stereochemistry = False

        return has_stereochemistry


def main():
    logging.getLogger("openff").setLevel(logging.ERROR)
    from pathlib import Path

    Path("./data-sets").mkdir(parents=True, exist_ok=True)

    default_filters = [
        RecordStatusFilter(status=RecordStatusEnum.complete),
        ConnectivityFilter(tolerance=1.2),
        UndefinedStereoFilter(),
    ]

    # Pull down the main torsion drive and optimization sets and filter out any records
    # which have not completed or which inadvertently contain intra-molecular h-bonds.
    client = FractalClient()

    torsion_set = TorsionDriveResultCollection.from_server(
        client=client,
        datasets=[
            "OpenFF Gen 2 Torsion Set 1 Roche 2",
            "OpenFF Gen 2 Torsion Set 2 Coverage 2",
            "OpenFF Gen 2 Torsion Set 3 Pfizer Discrepancy 2",
            "OpenFF Gen 2 Torsion Set 4 eMolecules Discrepancy 2",
            "OpenFF Gen 2 Torsion Set 5 Bayer 2",
            "OpenFF Gen 2 Torsion Set 6 supplemental 2",
        ],
        spec_name="default",
    )

    # Drop record ids with inconsistent optimization histories or which cause failures
    # in ForceBalance.
    torsion_set.entries[client.address] = [
        entry
        for entry in torsion_set.entries[client.address]
        if entry.record_id
        not in [
            "6098580",
            "2703504",
            "2703505",
            "18045478",
            # SMIRNOFF Coverage torsions set inconsistent IDs
            "2703253",
            "2703343",
            "2703386",
            "2703439",
            "2703449",
            "2703545",
            "2703546",
            "2703616",
            # from Gen3 set probably
            "35045000",
        ]
    ]

    torsion_set = torsion_set.filter(
        HydrogenBondFilter(method="baker-hubbard"),
        *default_filters,
        ElementFilter(
            # The elements supported by SMIRNOFF
            # Excluding Iodine here since we don't have Iodine torsions and any record with iodine is tainted on the
            # datasets listed above because of the auxiliary basis set issue
            allowed_elements=["H", "C", "N", "O", "S", "P", "F", "Cl", "Br"]
        )
    )

    with open("data-sets/td-set-for-fitting.json", "w") as file:
        file.write(torsion_set.json())

    opt_set_1 = OptimizationResultCollection.from_server(
        client=FractalClient(),
        datasets=[
            "OpenFF Gen 2 Opt Set 1 Roche",
            "OpenFF Gen 2 Opt Set 2 Coverage",
            "OpenFF Gen 2 Opt Set 3 Pfizer Discrepancy",
            "OpenFF Gen 2 Opt Set 4 eMolecules Discrepancy",
            "OpenFF Gen 2 Opt Set 5 Bayer",
        ],
        spec_name="default",
    )
    opt_set_1 = opt_set_1.filter(
        ElementFilter(
            # The elements supported by SMIRNOFF
            # Excluding Iodine here since we don't have Iodine torsions and any record with iodine is tainted on the
            # datasets listed above because of the auxiliary basis set issue
            # New sets added below in opt_set_2 has Iodine containing molecules that are safe
            allowed_elements=["H", "C", "N", "O", "S", "P", "F", "Cl", "Br"]
        ),
    )

    opt_set_1.entries[client.address] = [
        entry
        for entry in opt_set_1.entries[client.address]
        if entry.record_id not in ["2002949", "2002950"]
    ]

    opt_set_2 = OptimizationResultCollection.from_server(
        client=FractalClient(),
        datasets=[
            "OpenFF Gen2 Optimization Dataset Protomers v1.0",
            "OpenFF Iodine Chemistry Optimization Dataset v1.0",
        ],
        spec_name="default",
    )

    opt_set_2 = opt_set_2.filter(
        ElementFilter(
            # The elements supported by SMIRNOFF
            allowed_elements=["H", "C", "N", "O", "S", "P", "F", "Cl", "Br", "I"]
        ),
    )

    opt_set_1.entries["https://api.qcarchive.molssi.org:443/"].extend(
        opt_set_2.entries["https://api.qcarchive.molssi.org:443/"]
    )

    optimization_set = opt_set_1

    optimization_set = optimization_set.filter(
        RecordStatusFilter(status=RecordStatusEnum.complete),
        ConnectivityFilter(tolerance=1.2),
        UndefinedStereoFilter(),
        ConformerRMSDFilter(max_conformers=10),
    )

    with open("data-sets/opt-set-for-fitting.json", "w") as file:
        file.write(optimization_set.json())

    print("done!")


if __name__ == "__main__":
    main()
