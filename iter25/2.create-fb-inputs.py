import json
import os.path
from pathlib import Path

from openff.bespokefit.optimizers.forcebalance import ForceBalanceInputFactory
from openff.bespokefit.schema.fitting import (OptimizationSchema,
                                              OptimizationStageSchema)
from openff.bespokefit.schema.optimizers import ForceBalanceSchema
from openff.bespokefit.schema.smirnoff import (AngleHyperparameters,
                                               AngleSMIRKS,
                                               BondHyperparameters, BondSMIRKS,
                                               ImproperTorsionHyperparameters,
                                               ImproperTorsionSMIRKS,
                                               ProperTorsionHyperparameters,
                                               ProperTorsionSMIRKS)
from openff.bespokefit.schema.targets import (OptGeoTargetSchema,
                                              TorsionProfileTargetSchema,
                                              VibrationTargetSchema)
from openff.qcsubmit.results import (BasicResultCollection,
                                     OptimizationResultCollection,
                                     TorsionDriveResultCollection)
from openff.qcsubmit.results.filters import (ConformerRMSDFilter,
                                             ConnectivityFilter, ElementFilter,
                                             HydrogenBondFilter,
                                             RecordStatusFilter,
                                             ResultRecordFilter, SMARTSFilter,
                                             SMILESFilter)
from openff.toolkit.typing.engines.smirnoff import ForceField


def main():
    Path("./schemas/optimizations/").mkdir(parents=True, exist_ok=True)

    torsion_training_set = TorsionDriveResultCollection.parse_file(
        "data-sets/td-set-for-fitting.json"
    )

    # Filtering out unusual chemistries
    smarts_to_exclude = [
        "[#8+1:1]=[#7:2]",
        "[#15:1]=[#6:2]",
        "[#16+1:1]~[*:2]",
        "[*:1]=[#15:2]-[#7:3]~[*:4]",
        "[#17:1]~[#1:2]",
    ]
    torsion_training_set = torsion_training_set.filter(
        SMARTSFilter(smarts_to_exclude=smarts_to_exclude)
    )

    optimization_training_set = OptimizationResultCollection.parse_file(
        "data-sets/opt-set-for-fitting.json"
    )

    optimization_training_set = optimization_training_set.filter(
        SMARTSFilter(smarts_to_exclude=smarts_to_exclude)
    )
    # to pick initial values and parameters to optimize
    # enter
    custom_force_field = "modified-force-field-trained-on-sage-targets.offxml"
    initial_force_field = ForceField(
        "modified-force-field-trained-on-sage-targets.offxml"
    )
    initial_force_field.to_file(custom_force_field)
    # Define the parameters to train
    with open("data-sets/opt-set-angle-smirks.json") as file:
        angle_smirks = json.load(file)
    with open("data-sets/opt-set-bond-smirks.json") as file:
        bond_smirks = json.load(file)
    with open("data-sets/td-set-torsion-smirks.json") as file:
        torsion_smirks = json.load(file)
    with open("data-sets/improper-smirks.json") as file:
        improper_smirks = json.load(file)

    # a16, a17, a27, a35
    linear_angle_smirks = [
        "[*:1]~[#6X2:2]~[*:3]",  # a16
        "[*:1]~[#7X2:2]~[*:3]",  # a17
        "[*:1]~[#7X2:2]~[#7X1:3]",  # a27
        "[*:1]=[#16X2:2]=[*:3]",
    ]  # a35,

    target_parameters = [
        *[
            AngleSMIRKS(smirks=smirks, attributes={"k", "angle"})
            if smirks not in linear_angle_smirks
            else AngleSMIRKS(smirks=smirks, attributes={"k"})
            for smirks in angle_smirks["Angles"]
        ],
        *[
            BondSMIRKS(smirks=smirks, attributes={"k", "length"})
            for smirks in bond_smirks["Bonds"]
        ],
        *[
            ProperTorsionSMIRKS(
                smirks=smirks,
                attributes={
                    f"k{i + 1}"
                    for i in range(
                        len(
                            initial_force_field.get_parameter_handler("ProperTorsions")
                            .parameters[smirks]
                            .k
                        )
                    )
                },
            )
            for smirks in torsion_smirks["ProperTorsions"]
        ],
        *[
            ImproperTorsionSMIRKS(
                smirks=smirks,
                attributes={
                    f"k{i + 1}"
                    for i in range(
                        len(
                            initial_force_field.get_parameter_handler(
                                "ImproperTorsions"
                            )
                            .parameters[smirks]
                            .k
                        )
                    )
                },
            )
            for smirks in improper_smirks["ImproperTorsions"]
        ],
    ]

    # Define the full schema for the optimization.
    optimization_schema = OptimizationSchema(
        id="forcebalance-inputs",
        initial_force_field=os.path.abspath(custom_force_field),
        # Define the optimizer / ForceBalance specific settings.
        stages=[
            OptimizationStageSchema(
                optimizer=ForceBalanceSchema(
                    max_iterations=50,
                    step_convergence_threshold=0.01,
                    objective_convergence_threshold=0.1,
                    gradient_convergence_threshold=0.1,
                    n_criteria=2,
                    initial_trust_radius=-1.0,
                    extras={"wq_port": "55125", "asynchronous": "True"},
                ),
                # Define the torsion profile targets to fit against.
                targets=[
                    TorsionProfileTargetSchema(
                        reference_data=torsion_training_set,
                        energy_denominator=1.0,
                        energy_cutoff=5.0,
                        extras={"remote": "1"},
                    ),
                    OptGeoTargetSchema(
                        reference_data=optimization_training_set,
                        weight=0.1,
                        extras={"batch_size": 30, "remote": "1"},
                    ),
                ],
                # Define the parameters to refit and the priors to place on them.
                parameters=target_parameters,
                parameter_hyperparameters=[
                    AngleHyperparameters(priors={"k": 100, "length": 20}),
                    BondHyperparameters(priors={"k": 100, "length": 0.1}),
                    ProperTorsionHyperparameters(priors={"k": 1}),
                    ImproperTorsionHyperparameters(priors={"k": 1}),
                ],
            )
        ],
    )

    with open(
        os.path.join("./schemas", "optimizations", f"{optimization_schema.id}.json"),
        "w",
    ) as file:
        file.write(optimization_schema.json())

    # Generate the ForceBalance inputs
    ForceBalanceInputFactory.generate(
        os.path.join(optimization_schema.id),
        optimization_schema.stages[0],
        ForceField(optimization_schema.initial_force_field),
    )


if __name__ == "__main__":
    main()
