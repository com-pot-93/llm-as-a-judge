graph LR
  0:startEvent:(("startEvent")) --> 1:subProcess:("receive new potential job offers")
  1:subProcess:("receive new potential job offers") --> 5:task:("company confirmation of receiving job application")
  3:exclusiveGateway:{"x rate the company"} --> |"rated the company C or less"| 4:subProcess:("continue to receive job offers")
  4:subProcess:("continue to receive job offers") --> 5:task:("company confirmation of receiving job application")
  5:task:("company confirmation of receiving job application") --> 6:task:("company rates application")
  6:task:("company rates application") --> 7:task:("company want you to work for them")
  7:task:("company want you to work for them") --> 8:subProcess:("probation period starts")
  8:subProcess:("probation period starts") --> 9:subProcess:("probation period ends")
  8:subProcess:("probation period starts") --> 9:subProcess:("probation period ends")
  9:subProcess:("probation period ends") --> 10:task:("rate the company company rates you")
  10:task:("rate the company company rates you") --> 3:exclusiveGateway:{"x rate the company"}
  10:task:("rate the company company rates you") --> 11:intermediateCatchEvent:(("wait up to one year to se job application ratings"))
  11:intermediateCatchEvent:(("wait up to one year to se job application ratings")) --> 12:task:("stay to work permanently")