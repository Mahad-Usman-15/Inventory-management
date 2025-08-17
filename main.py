from dotenv import load_dotenv
import os
from pydantic import BaseModel
from agents import function_tool,Agent,OpenAIChatCompletionsModel,Runner, set_tracing_disabled
from openai import AsyncOpenAI

load_dotenv()
apikey=os.getenv("GEMINI_API_KEY")
BASEURL="https://generativelanguage.googleapis.com/v1beta/openai/"
set_tracing_disabled(disabled=True)
        
client=AsyncOpenAI(
    api_key=apikey,
    base_url=BASEURL
)
model=OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash",
)

inventory=[    {"id": 1, "name": "Basket", "quantity": 20},
    {"id": 2, "name": "chair", "quantity": 20},
    {"id": 3, "name": "Keyboard", "quantity": 10}]

# The schema for the function inputs is automatically created from the function's arguments

@function_tool
def add(name:str,id:int,quantity:int):
   global inventory
   """You have to add the user productname and product id to the inventory list
   Args
   name:str
   id :int
   """
   if not id or name or quantity :
      print ("id is needed to remove the product")
   pairs={"ProductId":id,"productName":name,"quantity":quantity}
   inventory.append(pairs)
   return f'Product {name} added with id {id}'

@function_tool
def modify(name:str,id:int,quantity:int):
   """You have to modify the product provided with product id
   
   Args
   name:str,
   id:int,
   quantity:int
   """
   if not id :
      print ("id is needed to remove the product")
   global inventory
   for product in inventory:
      if product.get("id")==id:
           new_product={"id":id,"name":name,"quantity":quantity}
           inventory[id]=new_product
      return f'Product with id{id} modified' 


@function_tool
def remove(id:int):
   global inventory
   if len(inventory)==0:
      return
   """You have to check whether the user defined productid exits in the inventory or not and remove if it 
    Args
   id :int
   """
   if not id :
      print ("id is needed to remove the product")
   for product in inventory:
      
    if product["id"]==id:
      inventory.remove(product)
    return f'Product with id{id} not found'
      
@function_tool
def listall():
   global inventory
   """You have to display all the inventory items if more than 0"""
   if len(inventory)>0:
      return inventory
   
   return "No items in the list" 

inventorymanagement=Agent(
   name="Inventory management",
   instructions="You have to manage inventory based on the user input add,remove,modify and listall using tools and  always tell the user the operation performed for eg product added",
   model=model,
   tools=[add,remove,listall,modify],
)
result =Runner.run_sync(
   inventorymanagement,
    input="add my product with id 4 Chai and quantity to 12",
 )


print(result.final_output)
print(inventory)






