import os
from dotenv import load_dotenv



# Now you can use `openai_api_key` to authenticate with the OpenAI API

import uvicorn
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from pydantic import BaseModel

system_prompt = """
"You are an expert in managing YouTube addiction, with a deep understanding of addiction psychology, goal-setting strategies, and behavior modification techniques. Your task is to create a personalized 30-day improvement plan for individuals seeking to balance their digital consumption with personal growth. You will receive input regarding the individual's personal goals and passions, alongside their specific goals for reducing YouTube usage and content they aim to avoid. Based on this information, you are to provide a detailed plan that includes:

Initial Assessment: Summarize the individual's current situation based on their input, highlighting key areas for improvement in their YouTube consumption habits and how these relate to their personal goals and passions.
Goal-Setting: Outline specific, measurable, achievable, relevant, and time-bound (SMART) goals for both reducing YouTube addiction and advancing towards their personal objectives.
Daily Action Steps: Provide a day-by-day guide for the 30-day period, with each day's activities designed to gradually reduce YouTube consumption and encourage progress on their personal goals. Include practical tips for avoiding triggers, managing cravings, and finding healthier alternatives.
Educational Insights: Integrate brief educational snippets about the psychology of addiction and the role of dopamine in habit formation, tailored to help the individual understand and navigate their journey.
Motivational Support: Offer motivational messages and affirmations to encourage persistence, resilience, and self-compassion throughout the 30-day plan.
Remember to approach this task with empathy, offering guidance that is both realistic and supportive, considering the individual's unique circumstances and challenges."
"""


prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)

planner_system_prompt = """
You transform a youtube addiction improvment plan to a structured data for a chrome extension. The result is in json format
the json object should contain 30 items from day_1 to day_30.
In each item there are three items
1. allowed_catagory: a list of video catagories that are related to the users goal
2. daily_limit: number that contains how many irrelevant videos are allowed today, follow the plan and gradually reduce the limit from 10 to 0
3. personal_goal: one action item for the personal goal, will be display to encourage user to work towards their goal
"""

json_prompt = ChatPromptTemplate.from_messages(
    [("system", planner_system_prompt), ("user", "{input}")]
)


class Data(BaseModel):
    personal_goal: str
    addiction_goal: str


@app.post("/data")
async def gpt35_turbo(data: Data,request:Request):
    print("ggk")
    body =await request.body()
    print(body.decode())
    
    gpt35_turbo = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0,)
    chain = prompt | gpt35_turbo
    result = chain.invoke(
        {
            "input": "Personal goal:"
            + data.personal_goal
            + " Addiction goal: "
            + data.addiction_goal
        }
    )
    gpt35_turbo_json = ChatOpenAI(
        model_name="gpt-3.5-turbo-0125",
        temperature=0,
    ).bind(response_format={"type": "json_object"})
    json_chain = json_prompt | gpt35_turbo_json
    plan = json_chain.invoke({"input": result})
    return {"result": result, "plan": plan}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

