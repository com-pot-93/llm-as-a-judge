graph LR
  0:task:("Send list [App]") -.-> 1:task:("Receive list [User]")
  0:task:("Send list [App]") --> 19:subProcess:("Process Selection [App]")
  1:task:("Receive list [User]") --> 2:task:("Check existing tools and materials [User]")
  3:task:("Send instructions [App]") -.-> 4:task:("Receive instructions [User]")
  3:task:("Send instructions [App]") --> 29:task:("Receive media [App]")
  4:task:("Receive instructions [User]") --> 5:task:("Repair [User]")
  5:task:("Repair [User]") --> 23:exclusiveGateway:{"x Repair successful [User]"}
  6:startEvent:(("startEvent [User]")) --> 7:task:("Enter model [User]")
  7:task:("Enter model [User]") --> 8:task:("Enter damage [User]")
  7:task:("Enter model [User]") -.-> 11:task:("Process model [App]")
  8:task:("Enter damage [User]") -.-> 9:task:("Process damage [App]")
  9:task:("Process damage [App]") --> 10:task:("Retrieve materials tools purchase and borrow sources [App]")
  14:exclusiveGateway:{"x Everything at home [User]"} --> |"No"| 15:inclusiveGateway:{"o [User]"}
  14:exclusiveGateway:{"x Everything at home [User]"} --> |"Yes"| 21:task:("Confirm acquisition closure [User]")
  15:inclusiveGateway:{"o [User]"} --> 16:task:("Contact friends [User]")
  15:inclusiveGateway:{"o [User]"} --> 17:task:("Buy at brick and mortar store [User]")
  15:inclusiveGateway:{"o [User]"} --> 18:task:("Buy via app [User]")
  16:task:("Contact friends [User]") --> 20:inclusiveGateway:{"o [User]"}
  17:task:("Buy at brick and mortar store [User]") --> 20:inclusiveGateway:{"o [User]"}
  18:task:("Buy via app [User]") -.-> 19:subProcess:("Process Selection [App]")
  18:task:("Buy via app [User]") --> 20:inclusiveGateway:{"o [User]"}
  19:subProcess:("Process Selection [App]") --> 22:task:("Receive message [App]")
  20:inclusiveGateway:{"o [User]"} --> 21:task:("Confirm acquisition closure [User]")
  21:task:("Confirm acquisition closure [User]") -.-> 22:task:("Receive message [App]")
  23:exclusiveGateway:{"x Repair successful [User]"} --> |"Yes"| 24:task:("Send media [User]")
  23:exclusiveGateway:{"x Repair successful [User]"} --> |"No"| 25:task:("Send to expert [User]")
  24:task:("Send media [User]") --> 26:inclusiveGateway:{"o [User]"}
  25:task:("Send to expert [User]") --> 31:endEvent:((("endEvent [User]")))
  26:inclusiveGateway:{"o [User]"} --> 27:task:("Send review [User]")
  26:inclusiveGateway:{"o [User]"} --> 28:task:("Send video [User]")
  27:task:("Send review [User]") -.-> 29:task:("Receive media [App]")
  27:task:("Send review [User]") --> 30:inclusiveGateway:{"o [User]"}
  28:task:("Send video [User]") -.-> 29:task:("Receive media [App]")
  28:task:("Send video [User]") --> 30:inclusiveGateway:{"o [User]"}
  30:inclusiveGateway:{"o [User]"} --> 31:endEvent:((("endEvent [User]")))