import re

officialNames = {'FSC':'Forward Scatter',
                 'SSC':'Side Scatter',
                 'FSCA':'Forward Scatter - Area',
                 'FSCH':'Forward Scatter - Height',
                 'FSCW':'Forward Scatter - Width',
                 'SSCA':'Side Scatter - Area',
                 'SSCH':'Side Scatter - Height',
                 'SSCW':'Side Scatter - Width',
                 'CD57':"beta-1,3-glucuronyltransferase 1 (glucuronosyltransferase P) or 'B3GAT1'",
                 'CD4':'CD4 molecule',
                 'Dump':'Dump',
                 'CD3':'part of the T cell receptor (TCR) complex',
                 'CD27':'CD27 molecule',
                 'TNF':'tumor necrosis factor',
                 'CD8':'CD8a molecule',
                 'IL2':'interleukin 2',
                 'CD45':"protein tyrosine phosphatase or 'PTPRC'",
                 'CD107':"lysosomal-associated membrane protein or 'LAMP1' and 'LAMP2'" ,
                 'IFNG':"interferon, gamma",
                 'IFNG+IL2':"interferon, gamma and interleukin 2",
                 'FL1H':'height of ffuorescence intensity',
                 'FL2H':'height of ffuorescence intensity', 
                 'FL3H':'height of ffuorescence intensity',
                 'FL4H':'height of ffuorescence intensity',
                 'FL1A':'area of ffuorescence intensity', 
                 'FL2A':'area of ffuorescence intensity', 
                 'FL3A':'area of ffuorescence intensity', 
                 'FL4A':'area of ffuorescence intensity', 
                 'Time':'Time',
                 'Unmatched':'no match'}   

def get_official_name_match(channel):
    strippedChannel = re.sub("\s|\-|\_","",channel)
    strippedChannel = strippedChannel.upper()
    
    if strippedChannel == 'FSCHEIGHT':
        return 'FSCH'
    if strippedChannel == 'FSCWIDTH':
        return 'FSCW'
    if strippedChannel == 'FSCAREA':
        return 'FSCA'

    if strippedChannel == 'SSCHEIGHT':
        return 'SSCH'
    if strippedChannel == 'SSCWIDTH':
        return 'SSCW'
    if strippedChannel == 'SSCAREA':
        return 'SSCA'

    if strippedChannel == 'IFN+IL2' or strippedChannel == "IFN+IL2PE":
        return 'IFNG+IL2'

    ## check for exact match 
    for key in officialNames.keys():    
        if strippedChannel == key.upper():
            return key
    ## check for similar match 
    for key in officialNames.keys():    
        if re.search(key,strippedChannel,flags=re.IGNORECASE):
            return key

    return 'Unmatched'
