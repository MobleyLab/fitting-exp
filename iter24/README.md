Includes the following improvements over Sage

- Starting point of Angles and Bonds from Modified seminario method which provides both equilibrium angles/lengths and forceconstants for each that are physically intuitive
- Including Dihedral ICs in opt-geo targets' contribution to objective function
- Optimizing impropers as well
- New torsion parameters to describe pyramidal bridgehead nitrogen chemistry (only optimizing with one optgeo target from vehicle set, opt-geo-batch-167/2054696-7)
- Some changes to general parameters to include the following chemistries
         modification: b43 changed from [#8X2:1]-[#8X2:2] to [#8X2:1]-[#8X2,#8X1-1:2] -->
         modification: b53 changed from [#16X2:1]-[#7:2] to [#16X2,#16X1-1:1]-[#7:2] -->
         modification: a18 changed from [*:1]-[#7X4,#7X3,#7X2-1:2]-[*:3] to [*:1]~[#7X4,#7X3,#7X2-1:2]~[*:3] -->
         modification: t51 changed from [*:1]-[#6X4:2]-[#7X3:3]-[*:4] to [*:1]~[#6X4:2]-[#7X3:3]~[*:4] -->
         modification: t130 changed from [*:1]-[#7X4,#7X3:2]-[#7X4,#7X3:3]-[*:4] to [*:1]~[#7X4,#7X3:2]-[#7X4,#7X3:3]~[*:4] -->
         modification: t138a as a child parameter to include [#7X2]-[#7X4] chemistry, other general force fields can parameterize this -->
         modification: new parameters for bridgehead Nitrogen chemistry based on t134 and t138 and tweaking the central Nitrogen to be 7x3 -->
         modification: t161 changed from "[*:1]~[#7X3:2]-[#15:3]~[*:4]" to "[*:1]~[#7:2]-[#15:3]~[*:4]" to make it more general -->

- Phosphorous torsion training target included (for t123) to alleviate the high gradients on angle parameter a40 that move the parameter values far away from expected values. 


Fitting wise the following options are chosen
- Larger priors on torsions to allow more variance to adjust to the MSM starting point
   priors
      Bonds/Bond/k :  100.0
      Bonds/Bond/length :  0.1
      Angles/Angle/k :  100.0
      Angles/Angle/angle :  20.0
      ProperTorsions/Proper/k :  15.0
      ImproperTorsions/Improper/k : 15.0
   /priors
   
- Change in weights on opt-geo-targets from 0.1 to 0.01 to be on the same scale as torsion targets after adding the Dihedral ICs to the objective function contribution

- Opt_geo_options - the weights for each internal coordinate (or the variance we can tolerate)
    $global
       bond_denom 0.05
       angle_denom 8.0
       dihedral_denom 15.0
       improper_denom 15.0
    $end

- Energy thresholds for torsion profile targets remain the same as before, a hard cutoff at 5 kcal/mol, and heavy weight to < 1 kcal/mol. 

- MSM starting points are obtained from Josh Horton's work: https://github.com/jthorton/MSM_QCArchive


