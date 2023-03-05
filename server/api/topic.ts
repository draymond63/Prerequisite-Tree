import { getTopicInfo } from "../utils";

// - Get Topic Info: Get description, image and title for a given list of topics
export default defineEventHandler(async (event): Promise<Topics | null> => {
  const input = await readBody(event); // TODO: Freezes on http method error
  const topics: string[] = Array.isArray(input) ? input : [input];
  if (topics[0] === "" || typeof topics[0] !== "string") {
    console.error("Invalid topic!:", topics);
    return null;
  }

  return Object.fromEntries(topics.map(title => [
    title,
    {
      "title": title,
      "image": "",
      "description": "Control theory is a field of control engineering and applied mathematics that deals with the control of dynamical systems in engineered processes and machines. The objective is to develop a model or algorithm governing the application of system inputs to drive the system to a desired state, while minimizing any delay, overshoot, or steady-state error and ensuring a level of control stability; often with the aim to achieve a degree of optimality.\nTo do this, a controller with the requisite corrective behavior is required. This controller monitors the controlled process variable (PV), and compares it with the reference or set point (SP). The difference between actual and desired value of the process variable, called the error signal, or SP-PV error, is applied as feedback to generate a control action to bring the controlled process variable to the same value as the set point. Other aspects which are also studied are  controllability and observability.  Control theory is used in control system engineering to design automation  that have revolutionized manufacturing, aircraft, communications and other industries, and created new fields such as robotics.  \nExtensive use is usually made of a diagrammatic style known as the block diagram. In it the transfer function, also known as the system function or network function, is a mathematical model of the relation between the input and output based on the differential equations describing the system.\nControl theory dates from the 19th century, when the theoretical basis for the operation of governors was first described by James Clerk Maxwell.  Control theory was further advanced by Edward Routh in 1874, Charles Sturm and in 1895, Adolf Hurwitz, who all contributed to the establishment of control stability criteria; and from 1922 onwards, the development of PID control theory by Nicolas Minorsky.\nAlthough a major application of mathematical control theory is in control systems engineering, which deals with the design of process control systems for industry, other applications range far beyond this. As the general theory of feedback systems, control theory is useful wherever feedback occurs - thus control theory also has applications in life sciences, computer engineering, sociology and operations research.\n\n",
    }
  ]));

  const topicInfo = await getTopicInfo(
    topics,
    ['extracts', 'pageimages'],
    { pllimit: '300' },
    3 // maxContinue
  );
  return Object.fromEntries(Object.entries(topicInfo).map(
    ([title, {description, image}]): [string, Topic] => [
      title,
      {
        title,
        description: description ?? "",
        image: image ?? "",
      }
    ]
  ));
});
