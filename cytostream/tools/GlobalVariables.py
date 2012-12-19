import re

officialNames = {'CD107':"lysosomal-associated membrane protein or 'LAMP1' and 'LAMP2'",
                 'CD27':'CD27 molecule',
                 'CD3':'Part of the T cell receptor (TCR) complex',
                 'CD4':'CD4 molecule',
                 'CD45':"protein tyrosine phosphatase or 'PTPRC'",
                 'CD57':"beta-1,3-glucuronyltransferase 1 (glucuronosyltransferase P) or 'B3GAT1'",
                 'CD8':'CD8a molecule',                
                 'Dump':'Dump',
                 'FL1H':'height of fuorescence intensity',
                 'FL2H':'height of fuorescence intensity', 
                 'FL3H':'height of fuorescence intensity',
                 'FL4H':'height of fuorescence intensity',
                 'FL1A':'area of fuorescence intensity', 
                 'FL2A':'area of fuorescence intensity', 
                 'FL3A':'area of fuorescence intensity', 
                 'FL4A':'area of fuorescence intensity',                 
                 'FSC':'Forward Scatter',
                 'IL2':'interleukin 2',
                 'IFNG':"interferon, gamma",
                 'IFNG+IL2':"interferon, gamma and interleukin 2",
                 'FSCA':'Forward Scatter - Area',
                 'FSCH':'Forward Scatter - Height',
                 'FSCW':'Forward Scatter - Width',
                 'SSC':'Side Scatter',
                 'SSCA':'Side Scatter - Area',
                 'SSCH':'Side Scatter - Height',
                 'SSCW':'Side Scatter - Width',
                 'TNF':'tumor necrosis factor',
                 'Time':'Time',
                 'Unmatched':'no match'}   

def get_official_name_match(channel):
    strippedChannel = re.sub("\s|\-|\_","",channel)
    strippedChannel = strippedChannel.upper()

    ## case specific    
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
    elif re.search("IFN",strippedChannel) and re.search("IL2",strippedChannel):
        return 'IFNG+IL2'

    sc = strippedChannel
    if re.search("CD14",sc) and re.search("CD19",sc) and re.search("AMINE",sc):
        return 'Dump'

    ## check for exact match 
    for key in officialNames.keys():    
        if strippedChannel == key.upper():
            return key
    ## check for similar match 
    for key in officialNames.keys():    
        if re.search(key,strippedChannel,flags=re.IGNORECASE):
            return key

    return 'Unmatched'
