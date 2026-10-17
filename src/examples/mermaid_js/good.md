graph LR
  0:startEvent:(("Problem with smartphone")) --> 1:task:("Enter the model and what is broken")
  1:task:("Enter the model and what is broken") --> 4:task:("Analyse defected parts")
  2:exclusiveGateway:{"x Is another part needed"} --> |"no"| 3:task:("Check if demanded tools are already at home")
  2:exclusiveGateway:{"x Is another part needed"} --> |"yes"| 4:task:("Analyse defected parts")
  3:task:("Check if demanded tools are already at home") --> 10:exclusiveGateway:{"x All tools at home"}
  4:task:("Analyse defected parts") --> 5:parallelGateway:{"+"}
  5:parallelGateway:{"+"} --> 6:task:("Create list of materials for one part")
  5:parallelGateway:{"+"} --> 7:task:("Create list of tools for one part")
  6:task:("Create list of materials for one part") --> 8:parallelGateway:{"+"}
  7:task:("Create list of tools for one part") --> 8:parallelGateway:{"+"}
  8:parallelGateway:{"+"} --> 9:task:("give ordering choices for one part")
  9:task:("give ordering choices for one part") --> 2:exclusiveGateway:{"x Is another part needed"}
  10:exclusiveGateway:{"x All tools at home"} --> |"no"| 11:task:("Contact friends if you can buy borrow from them")
  10:exclusiveGateway:{"x All tools at home"} --> |"yes"| 19:endEvent:((("Phone repaired")))
  11:task:("Contact friends if you can buy borrow from them") --> 12:exclusiveGateway:{"x Got all tools"}
  12:exclusiveGateway:{"x Got all tools"} --> 13:task:("Order needed tools")
  12:exclusiveGateway:{"x Got all tools"} --> |"yes"| 19:endEvent:((("Phone repaired")))
  13:task:("Order needed tools") --> 14:task:("Receive instructions")
  14:task:("Receive instructions") --> 15:exclusiveGateway:{"x Did it work"}
  15:exclusiveGateway:{"x Did it work"} --> |"no"| 16:task:("Send Smartphone to an expert")
  15:exclusiveGateway:{"x Did it work"} --> |"yes"| 17:task:("Send review")
  16:task:("Send Smartphone to an expert") --> 18:exclusiveGateway:{"x"}
  17:task:("Send review") --> 18:exclusiveGateway:{"x"}
  18:exclusiveGateway:{"x"} --> 19:endEvent:((("Phone repaired")))