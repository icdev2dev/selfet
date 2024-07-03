import asyncio
from bmodels import AutoExecAssistant

async def monitor_assistant(assistant_id, entity_list):
    while True:
        print (f"from moni {entity_list}")
        if assistant_id not in entity_list:
            break
        await asyncio.sleep(1) 


async def resource_watcher(task_queue, entity_list):
    while True:
        
        autoexecassistant_list = AutoExecAssistant.list()

        if len(entity_list) == 0 and len(autoexecassistant_list) != 0: 
           
               entity_list.append(autoexecassistant_list[0].id)
               monitor_assistant_task = asyncio.create_task(monitor_assistant(autoexecassistant_list[0].id, entity_list))
               task_queue.append(monitor_assistant_task)


        if len(autoexecassistant_list) == 0 and len(entity_list) != 0:
            _ = entity_list.pop()

        print(entity_list)

        await asyncio.sleep(5)



async def main():
    task_queue = []
    entity_list = []

    resource_watcher_task = asyncio.create_task (resource_watcher(task_queue=task_queue, entity_list=entity_list))
    task_queue.append(resource_watcher_task)
    await asyncio.gather(*task_queue)



def run_main():
    asyncio.run(main=main())


if __name__ == "__main__":
    run_main()
