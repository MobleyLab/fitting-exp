This optimization begins from the force field produced in the `vdw-v1` directory, whereby the
vdW parameters are re-fit. It can be re-run by first running the

```shell
ForceBalance optimize.in
```

command. 

The current input files attempt to run `ForceBalance` in a distributed fashion using the
`Work Queue` framework. This requires spawning work queue workers which will connect to 
the main `ForceBalance` command

```shell
~/opt/cctools/current/bin/work_queue_worker -t 800000 ls07 55125
```

More information about running `ForceBalance` using work queue [can be found here](
https://github.com/openforcefield/openforcefield-forcebalance/blob/master/setup_guide.md#step-3-install-and-usage-of-work-queue-from-cctools-optional
)
