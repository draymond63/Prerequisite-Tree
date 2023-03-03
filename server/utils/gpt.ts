import { Configuration, OpenAIApi } from "openai";
import { APIStatus } from './index';

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

export const queryGPT = async (prompt: string): Promise<[string, APIStatus]> => {
  if (!configuration.apiKey) {
    return ['', APIStatus.INVALID_INPUT];
  }

//   return [` Chemistry                                                                                                             11:53:16  
// 2. Science
// 3. Scientific Method
// 4. Technology
// 5. Mathematics (Calculus)`, APIStatus.OKAY];

  try {
    const completion = await openai.createCompletion({
      model: "text-davinci-003",
      prompt: prompt,
      temperature: 0,
      max_tokens: 256, // TODO: Parameterize conditions?
      top_p: 1,
      frequency_penalty: 0.3,
      presence_penalty: 0,
      stop: ["11."]
    });
    return [completion.data.choices[0].text ?? '', APIStatus.OKAY];
  } catch(error: any) {
    if (error?.response) {
      console.error('Error with OpenAI API request:', error.response.status, error.response.data);
      return [`${error?.response}`, APIStatus.UNKNOWN_FAILURE];
    } else {
      console.error(`Error with OpenAI API request: ${error?.message}`);
      return [`${error?.message}`, APIStatus.UNKNOWN_FAILURE];
    }
  }
}

// TODO: Make prompt
export const getPrereqsPrompt = (topic: string, options: string[]): string => {
  console.log(options);
  return `The following is a list of topics related to "${topic}". 

${options.join('\n')}

The following is a list of the five most relevant prerequisites for "${topic}". All prerequisites are from the list above:
1.`;
}

export const parseList = (response: string): string[] => {
  const lines = response.split(/\n/);
  return lines.map(line => {
    const parts = line.split(/\s*\.\s*/);
    if (parts.length === 2) {
      return parts[1].trim();
    } else {
      return parts[0].trim();
    }
  });
}