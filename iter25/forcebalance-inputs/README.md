- Priors in
```
  priors
     Angles/Angle/k :  100.0
     Angles/Angle/angle :  20.0
     Bonds/Bond/k :  100.0
     Bonds/Bond/length :  0.1
     ProperTorsions/Proper/k :  1.0
     ImproperTorsions/Improper/k :  1.0
  /priors
  ```

- Target options
```
  $global
  bond_denom 0.05
  angle_denom 8.0
  dihedral_denom 15.0
  improper_denom 15.0
  $end
```  
- Datasets used in training
```  
  Excluding Iodine from Gen2 sets,
    Torsions:
            "OpenFF Gen 2 Torsion Set 1 Roche 2",
            "OpenFF Gen 2 Torsion Set 2 Coverage 2",
            "OpenFF Gen 2 Torsion Set 3 Pfizer Discrepancy 2",
            "OpenFF Gen 2 Torsion Set 4 eMolecules Discrepancy 2",
            "OpenFF Gen 2 Torsion Set 5 Bayer 2",
            "OpenFF Gen 2 Torsion Set 6 supplemental 2",

    Optimized-geometries:
            "OpenFF Gen 2 Opt Set 1 Roche",
            "OpenFF Gen 2 Opt Set 2 Coverage",
            "OpenFF Gen 2 Opt Set 3 Pfizer Discrepancy",
            "OpenFF Gen 2 Opt Set 4 eMolecules Discrepancy",
            "OpenFF Gen 2 Opt Set 5 Bayer",
       
  With Iodine containing molecules:
    Optimized-geometries:
            "OpenFF Gen2 Optimization Dataset Protomers v1.0",
            "OpenFF Iodine Chemistry Optimization Dataset v1.0"
```
