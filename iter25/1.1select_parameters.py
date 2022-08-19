import copy
import functools
import json
import logging
from collections import defaultdict
from multiprocessing import Pool
from tempfile import NamedTemporaryFile

from openff.qcsubmit.results import (OptimizationResultCollection,
                                     TorsionDriveResultCollection)
from openff.qcsubmit.results.filters import (ConformerRMSDFilter,
                                             ConnectivityFilter, ElementFilter,
                                             HydrogenBondFilter,
                                             RecordStatusFilter,
                                             ResultRecordFilter, SMARTSFilter)
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


def label_ids(record_and_molecule, force_field, parameter_types):
    record, molecule = record_and_molecule

    full_labels = force_field.label_molecules(molecule.to_topology())[0]

    parameter_ids = set()

    for parameter_type in parameter_types:

        parameter_labels = full_labels[parameter_type]

        for indices, parameter in parameter_labels.items():

            if isinstance(record, TorsionDriveRecord) and {*indices[1:3]} != {
                *record.keywords.dihedrals[0][1:3]
            }:
                continue

            parameter_ids.add(parameter.id)

    return [*parameter_ids]


def select_parameters(training_set, parameter_types, output_path, force_field):
    # Print out coverage information.
    coverage = defaultdict(int)

    with Pool(8) as pool:

        for parameter_ids in tqdm(
            pool.imap(
                functools.partial(
                    label_ids, force_field=force_field, parameter_types=parameter_types
                ),
                training_set.to_records(),
            ),
            total=training_set.n_results,
        ):

            for parameter_id in parameter_ids:
                coverage[parameter_id] += 1

    # Save out the SMIRKS which should be trained against this set.
    with open(output_path, "w") as file:

        selected_parameters = defaultdict(list)

        for parameter_type in parameter_types:

            for parameter_id, count in coverage.items():

                found_parameters = force_field.get_parameter_handler(
                    parameter_type
                ).get_parameter({"id": parameter_id})

                if count < 5 or len(found_parameters) == 0:
                    print("Low number of targets for ", parameter_id, count)
                    continue

                selected_parameters[parameter_type].append(found_parameters[0].smirks)

        json.dump(selected_parameters, file)


def main():
    logging.basicConfig(level=logging.INFO)

    custom_force_field = "modified-force-field-trained-on-sage-targets.offxml"
    initial_force_field = ForceField(custom_force_field)

    torsion_set = TorsionDriveResultCollection.parse_file(
        "data-sets/td-set-for-fitting.json"
    )

    select_parameters(
        torsion_set,
        parameter_types=["ProperTorsions"],
        output_path="data-sets/td-set-torsion-smirks.json",
        force_field=initial_force_field,
    )

    # opt_set = OptimizationResultCollection.parse_file("data-sets/opt-set-for-fitting.json")

    # select_parameters(
    #   opt_set,
    #   parameter_types=["Bonds"],
    #   output_path="data-sets/opt-set-bond-smirks.json",
    #   force_field=initial_force_field,
    # )

    # select_parameters(
    #   opt_set,
    #   parameter_types=["Angles"],
    #   output_path="data-sets/opt-set-angle-smirks.json",
    #   force_field=initial_force_field,
    # )


if __name__ == "__main__":
    main()
