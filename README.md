So I wanted to create a ImageProcessing Pipeline without 

The design: 

We have a Thread that contains a reference to another thread and an optional assistant


class AutoExecThread(BaseThread): 
    

We make use of betaassi to subclass BaseThread for this purpose.
