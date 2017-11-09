Name: Subas Benakatti
Email: subas.benakatti@gmail.com


INPUTS:

Script Need following inputs
	1. Input Patran output report file (Format of the report file is shown below)
	2. Patran group session file.
	3. Optional: Name of the Group (Element connected CFAST) if you want to omit strain in the elements connected to CFAST.

Patran Rpt file format:
                       MSC.Patran 19.1.164499 Mon Oct 15 14:16:55 PDT 2012 - Analysis Code: MSC.Nastran 
                           Load Case: SC12345678: xyz 
                                             Result Strain Tensor,  - Layer At Z1 
                                                     Entity: Element Tensor


-Entity ID---Max Principal 2D--Min Principal 2D-
    1100000        5.128321        -11.392458
    1100001        7.894047        -20.769062
    1100002        6.266325        -16.393766
    1100003        7.110971         -0.126525
    1100004        1.263338        -11.550056
    1100005        5.348788         -0.332084
    1100006        2.289480         -7.473336
    1100007        1.785023         -2.163985
    1100008        7.010223         -2.652127
    1100009        1.945845         -8.329074
	
OUTPUTFILE:
	1. PRT FILE NAME +'_StrainResults.txt' : Critical Strain results for each group availabe in the input 2. 
											If element results missing in Input 1, Missing element results information is written in the Output file 3.
	2. PRT FILE NAME +'_summary.txt' : Critical strain results for each elements in the Input file 1.
	3. PRT FILE NAME +'_logfile.txt' : information about missing element results
	
Example of the OUTPUT1:
GroupName	 MaxP ElementID	MaxPrincipalStrain	MaxP LoadCase	MinP ElementID	MinPrincipalStrain	MinP LoadCaseID
ElmGroup_1	1123330	2082.733643	80000051Z1	1123330	-2914.169922	80000071Z1
ElmGroup_3	1427417	2031.940063	80000051Z2	1427417	-2147.699219	80000071Z2
ElmGroup_5	1224102	2470.303223	80000051Z1	1224102	-3442.213623	80000071Z1


Example of the OUTPUT2:
ElementID	MaxPrincipalStrain	MaxP LoadCase	MinPrincipalStrain	MinP LoadCase
1100000	481.956146	80000051Z1	-692.825317	80000071Z1
1100001	403.381805	80000051Z2	-550.497681	80000071Z2
1100002	449.441345	80000051Z2	-628.361938	80000071Z2
1100003	635.158630	80000051Z2	-904.782104	80000071Z2
1100004	500.561493	80000051Z2	-699.610657	80000071Z2
1100005	410.834991	80000051Z2	-579.644287	80000071Z2
1100006	468.812378	80000051Z1	-660.778748	80000071Z1

Example of the OUTPUT3:
Group: ElmGroup_2 not analyses, All Elements results not availabe in input RPT
Group: ElmGroup_4 not analyses, All Elements results not availabe in input RPT
In Group: ElmGroup_5 Element: 1250000 results not availabe in input RPT

