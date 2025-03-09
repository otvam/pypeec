# Security Policy

To report a security issue, please email [guillod@otvam.ch](mailto:guillod@otvam.ch).
Please include a description of the issue, the steps you took to create the issue, 
the affected versions, and, if known, mitigations for the issue. 

The fact that PyPEEC can use Pickle files for storing the mesher and solver results
is an accepted trade-off and is not considered as a security issue. Alternatively, 
JSON/MessagePack files can be used for storing the results.