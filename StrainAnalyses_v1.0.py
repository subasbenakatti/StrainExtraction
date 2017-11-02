import os
import re
import sys


# List Substract Function
def ListA_minus_B(A,B):
	#C=[item for item in A if item not in B]
	C= list(set(A).difference(set(B)))
	return C

#=============================================================================================================================================
# return the dict Summary{elm1:[elm1, MaxP strain, LC, MinP Strain, LC],elm2:......}
#
def ExtractCriticalStrain(RptFile):
	Strain ={}
	Loadcase ='NILL'
	LoadCaseList =[]
	for line in open(RptFile):
		#Read Elements Results
		if re.match(r'^\s+(\d+)\s+(\S+)\s+(\S+)\s*$',line,re.M):
			ResultsMatch = re.match(r'^\s+(\d+)\s+(\S+)\s+(\S+)\s*$',line,re.M)
			if key not in Strain.keys():
				Strain[key]={}
			Strain[key][ResultsMatch.group(1)]=[]
			Strain[key][ResultsMatch.group(1)]=(line.strip().split())

		#Load case identification
		elif re.match(r'(\s+Load Case: SC)(\d+)(: )(A320\w{3})(.*)',line,re.M):
			LoadCaseMatch = re.match(r'(\s+Load Case: SC)(\d+)(: )(A320\w{3})(.*)',line,re.M)
			if LoadCaseMatch.group(4) == 'A320NEO':
				Loadcase = LoadCaseMatch.group(2)+"1"
			elif LoadCaseMatch.group(4) == 'A320SHA':
				Loadcase = LoadCaseMatch.group(2)+"2"
			else:
				Loadcase = LoadCaseMatch.group(2)
		
		#Layer identification		
		elif re.match(r'(\s+Result Strain Tensor,  - Layer At Z)(\d)(.*)',line,re.M):
			LayerMatch = re.match(r'(\s+Result Strain Tensor,  - Layer At )(\S+)(.*)',line,re.M)
			Layer = LayerMatch.group(2)
			key = Loadcase + Layer
			print(Loadcase ,Layer)
			LoadCaseList.append(key)

	ElementList = Strain[LoadCaseList[0]].keys()
	Summary={}
	for Elm in ElementList:
		Summary[Elm]=[]
		MaxP = [float(Strain[LC][Elm][1]) for LC in LoadCaseList]
		MinP = [float(Strain[LC][Elm][2]) for LC in LoadCaseList]
		Summary[Elm]=[Elm, max(MaxP),LoadCaseList[MaxP.index(max(MaxP))], min(MinP),LoadCaseList[MinP.index(min(MinP))]]
	
	OutFile = open(RptFile.replace('.rpt','')+'_summary.txt','w')
	OutFile.write('ElementID\tMaxPrincipalStrain\tMaxP LoadCase\tMinPrincipalStrain\tMinP LoadCase\n')
	for elm in Summary:
		OutFile.write('%s\t%f\t%s\t%f\t%s\n'%(Summary[elm][0],Summary[elm][1],Summary[elm][2],Summary[elm][3],Summary[elm][4]))
	OutFile.close()
	print('Rpt file processed:')
	return Summary

#=============================================================================================================================================
# return the dict PatGroup{Group1:{Element:[.....],Node:[....],....},Group2:{Element:[.....],Node:[....],....},....}
#	
def ReadPatranSesFile(SesionFile):
	Group={}
	String =''
	GroupName = 'NILL'
	for line in open(SesionFile):
		if line[0]!="$":
			if re.match(r'^ga_group_entity_add\S\s*\"(\S+)", "(.*)(" // @)$',line):
				MatchGroup= re.match(r'^ga_group_entity_add\S\s*\"(\S+)", "(.*)(" // @)$',line)
				String = MatchGroup.group(2)
				GroupName=MatchGroup.group(1)
			elif re.match(r'^ga_group_entity_add\S\s*\"(\S+)", "(.*)\" \)$',line):
				MatchGroup= re.match(r'ga_group_entity_add\S\s*\"(\S+)", "(.*)\" \)$',line)
				String = MatchGroup.group(2)
				GroupName=MatchGroup.group(1)
				Group[GroupName]=String
			elif re.match(r'^\"(.*)(" // @)$',line):
				MatchGroup= re.match(r'^\"(.*)(" // @)$',line)
				String=String +MatchGroup.group(1)
			elif re.match(r'^\"(.*)\"\s\)',line):
				MatchGroup= re.match(r'^\"(.*)\"\s\)',line)
				String=String +MatchGroup.group(1)
				Group[GroupName]=String
			elif re.match(r'^ga_group_entity_add\S\s*\"(\S+)",  @',line):
				MatchGroup= re.match(r'^ga_group_entity_add\S\s*\"(\S+)",  @',line)
				GroupName=MatchGroup.group(1)

	#Progess the Patran Group Element
	PatranGroup={}
	for key in Group:
		#OutputFile.write('%s%s\n'%(key,Group[key]))
		LineSplit=Group[key].split(' ')
		PatranGroup[key]={}
		card = 'Error'
		for x in LineSplit:
			#if re.match(r'([a-z]*)',x):
			if x.isalpha():
				card=x
				PatranGroup[key][card]=[]
			elif re.match(r'(\d+):(\d+):(\d+)',x):
				EntityMatch=re.match(r'(\d+):(\d+):(\d+)',x)
				PatranGroup[key][card].extend(range(int(EntityMatch.group(1)),int(EntityMatch.group(2))+int(EntityMatch.group(3)),int(EntityMatch.group(3))))
			elif re.match(r'(\d+):(\d+)',x) :
				EntityMatch=re.match(r'(\d+):(\d+)',x)
				PatranGroup[key][card].extend(range(int(EntityMatch.group(1)),int(EntityMatch.group(2))+1,1))
			elif re.match(r'(\d+)',x):
				PatranGroup[key][card].append(int(x))
			else :
				#print('Please check entity [%s] in the group [%s]'%(x,key))
				continue
		if 'Error' in PatranGroup[key].keys():
			print('Please check the group: %s . its has entery : %s'%(key,PatranGroup[key]['Error']))
	print('Patran group session file processed:')
	return PatranGroup

#==========================================================================================================================================================================
# Function finds the Critical Strain results for each group	
#
def StrainAnalyses():
	RptFile =input('Enter Patran RPT File Name:')
	SesionFile = input('Enter Patran Session File Name:')
	ConnCHK = input('Element Connected to CFSAT should be removed?(YES/NO):')	
	Group = ReadPatranSesFile(SesionFile)
	# Condition to exclude cfast connected element 
	if ConnCHK == 'YES':
		ConnGrp = input('Element Connected to CFSAT Group Name:')
		if ConnGrp not in Group.keys():
			print('Input group Element Connected to CFSAT is missing in Patran session file')
			sys.exit(1)
	else:
		ConnGrp = 'NILL'
	# Extract critical strain results for each element	
	StrainSummary = ExtractCriticalStrain(RptFile)
	ResultsElementsList = [int(key) for key in StrainSummary.keys()]
	# find the critical results for each group
	ResultsSummary={}
	# Condition to exclude cfast connected element 
	LogFile = open(RptFile.replace('.rpt','')+'_logfile.txt','w')
	if ConnGrp != 'NILL':
		for grp in Group:
			if 'Element' not in Group[grp].keys():
				LogFile.write('Group: %s not analyses, Elements are not defined in the group\n' %grp)
				continue
			else:
				MissingElm = ListA_minus_B(Group[grp]['Element'],ResultsElementsList)
				if len(MissingElm) == len(Group[grp]['Element']) :
					LogFile.write('Group: %s not analyses, All Elements results not availabe in input RPT\n' %grp)
					continue
				elif len(MissingElm)> 0 :
					for Melm in MissingElm:
						LogFile.write('In Group: %s Element: %s results not availabe in input RPT\n' %(grp,Melm))
					Group[grp]['Element'] = ListA_minus_B(Group[grp]['Element'],MissingElm)
			
			ResultsSummary[grp]=[]
			ElList = [StrainSummary[str(elm)][0] for elm in Group[grp]['Element'] if elm not in Group[ConnGrp]['Element']]
			MaxP = [StrainSummary[str(elm)][1] for elm in Group[grp]['Element'] if elm not in Group[ConnGrp]['Element']]
			MaxPLC = [StrainSummary[str(elm)][2] for elm in Group[grp]['Element']if elm not in Group[ConnGrp]['Element']]
			MinP = [StrainSummary[str(elm)][3] for elm in Group[grp]['Element'] if elm not in Group[ConnGrp]['Element'] ]
			MinPLC = [StrainSummary[str(elm)][4] for elm in Group[grp]['Element'] if elm not in Group[ConnGrp]['Element']]
			ResultsSummary[grp]=[ElList[MaxP.index(max(MaxP))], max(MaxP),MaxPLC[MaxP.index(max(MaxP))],ElList[MinP.index(min(MinP))], min(MinP),MinPLC[MinP.index(min(MinP))]]
	else:
		for grp in Group:
			if 'Element' not in Group[grp].keys():
				LogFile.write('Group: %s not analyses, Elements are not defined in the group\n' %grp)
				continue
			else:
				MissingElm = ListA_minus_B(Group[grp]['Element'],ResultsElementsList)
				if len(MissingElm) == len(Group[grp]['Element']) :
					LogFile.write('Group: %s not analyses, All Elements results not availabe in input RPT\n' %grp)
					continue
				elif len(MissingElm)> 0 :
					for Melm in MissingElm:
						LogFile.write('In Group: %s Element: %s results not availabe in input RPT\n' %(grp,Melm))
					Group[grp]['Element'] = ListA_minus_B(Group[grp]['Element'],MissingElm)
					
			ResultsSummary[grp]=[]
			ElList = [StrainSummary[str(elm)][0] for elm in Group[grp]['Element']]
			MaxP = [StrainSummary[str(elm)][1] for elm in Group[grp]['Element'] ]
			MaxPLC = [StrainSummary[str(elm)][2] for elm in Group[grp]['Element']]
			MinP = [StrainSummary[str(elm)][3] for elm in Group[grp]['Element']]
			MinPLC = [StrainSummary[str(elm)][4] for elm in Group[grp]['Element']]
			ResultsSummary[grp]=[ElList[MaxP.index(max(MaxP))], max(MaxP),MaxPLC[MaxP.index(max(MaxP))],ElList[MinP.index(min(MinP))], min(MinP),MinPLC[MinP.index(min(MinP))]]
	
	OUT=open(RptFile.replace('.rpt','')+'_StrainResults.txt','w')
	OUT.write('GroupName\t MaxP ElementID\tMaxPrincipalStrain\tMaxP LoadCase\tMinP ElementID\tMinPrincipalStrain\tMinP LoadCaseID\n')
	for key in ResultsSummary:
		OUT.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(key,ResultsSummary[key][0],ResultsSummary[key][1],ResultsSummary[key][2],ResultsSummary[key][3],ResultsSummary[key][4],ResultsSummary[key][5]))
	OUT.close()
	print('Strain Processing completed')
	
StrainAnalyses()
