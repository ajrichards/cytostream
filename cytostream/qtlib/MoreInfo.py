#!/usr/bin/env python


moreInfoDict = {
    "Data Processing":
    """<br><h2>Data Processing</h2>
       <br>The upper table or channel table:
       <ul>
       <li><b>channel</b>   - select the channels that you would like to include when the model is run.</li> 
       <li><b>original</b>  - this is the channel name that was extracted from the fcs file. (not editable)</li>
       <li><b>alternate</b> - for figures and reports if you would like to rename the original channels then edit these cells</li>
       <li><b>official</b>  - cytostream trys to match the channel names to a Gene Symbol or another name.  Ensure these make sense.</li>
       </ul>

   <p>For the lower table the column <b>alternate</b> is available to rename files for reporting and plotting.

   <p>It is important to note that all FCS files in a project are assumed to have the same channels
       and same channel order.  If this is not true then use more than one project""" 
}
