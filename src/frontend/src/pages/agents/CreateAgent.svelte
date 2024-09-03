<script>
    import { Router, Route, Link, useLocation } from "svelte-routing";
    import AgentBackgroundPage from "./createagent/AgentBackground.svelte";
    import AgentTemplatePage from "./createagent/AgentTemplate.svelte";
    import AgentWorkflowPage from "./createagent/AgentWorkflow.svelte";


    const agentTypes  = ["Creator", "Reviewer"]



    let subTabs = [
        {name: 'Agent Background', route: 'agentBackground', component: AgentBackgroundPage},
        {name: 'Agent Template', route: 'agentTemplate', component: AgentTemplatePage},
        {name: 'Agent Workflow', route: 'agentWorkflow', component: AgentWorkflowPage},
    ];
 
    let boxText = "Agent Configuration";

    let selectedAgentType = "Creator"

    const location = useLocation()

    

    function handleSelectedAgentChange()  {

    }

</script>

<div class="container">

    <div class="vertical-selects-main">

        <div class="horizontal-elements">
            <div class="vertical-selects-main">

                <div class="horizontal-elements">                
                    <div> Agent Type </div>
                    <div>
                        <select bind:value={selectedAgentType} on:change={handleSelectedAgentChange}>
                            {#each agentTypes as agentType}
                                <option value={agentType}>{agentType}</option>
                            {/each}
                        </select>
                    </div>
                </div>


                <div class="horizontal-elements">
                    <div> Agent Name</div>
                    <div>
                        <textarea></textarea>
                    </div>
                </div>


            </div>

            <div class="horizontal-elements">
                <div> Agent Description </div>
                <div>
                    <textarea style="width: 900px; height: 100px"> </textarea>
                </div>
            </div>

            
        </div>


        <div class="box">
            <span class="box-text">{boxText}</span>
            <!-- Additional content inside the box -->
            <div class="vertical-selects">
                <div class="horizontal-elements">
                    <Router>
                        <div class="sub-container">
                            <div class="sub-sidebar">
                                <ul>
                                    {#each subTabs as subTab}
                                        <li class:selected={$location.pathname.includes(subTab.route)}>
                                            
                                                                                            
                                            <Link to={subTab.route}  >
                                            {subTab.name}
                                            
                                            </Link>
                                        
                                        </li>
                                    {/each}
                                </ul>
                            </div>
                            
                            <div class="sub-main-content">
                                {#each subTabs as subTab}
                                    <Route path={subTab.route} component={subTab.component} />
                                {/each}
                            </div>
                        </div>
                    </Router>                
                </div>
            </div>
            
        </div>

        <div class="horizontal-elements">
            <button> Save</button>
            <button> Cancel </button>    
        </div>

    </div>

</div>

<style>


    .container {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            border-spacing: 1cm;
            outline: auto;
            height: 100%
        }


    .sub-container {
            display: flex;
            flex-direction: row;  /* Stack sidebar and content vertically */
    }


    .sub-sidebar {
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Align items to the start (left) */
    }


    .sub-sidebar ul {
        display: flex;
        flex-direction: column; /* Stack the list items vertically */
        list-style-type: none;
        text-align: left;

    }
    

    .sub-sidebar li {
        margin-right: 20px; /* Space between links */
        flex-direction: column;
    }


    .sub-sidebar li.selected  {
        background-color: hsl(220, 2%, 74%); /* Highlighted background for the selected tab */
    }



    .box {
        position: relative;
        width: 100%; /* Adjust the width as needed */
        height: 350px; /* Adjust the height as needed */
        border: 2px solid #ded6d6;
        padding: 5px;
        box-sizing: border-box;
    }

    .box-text {
        position: absolute;
        top: -10px; /* Adjust to position above the box */
        left: 10px;
        background-color: hwb(0 81% 16%); /* Ensure the text is readable */

        color: black;
        padding: 0 5px;
    }
    .vertical-selects-main {
        display: block;
        width: 100%; /* Optional: to make the select elements full-width */
        height: auto;
        margin-bottom: 5x; /* Optional: add space between the selects */
        margin-right: 10px;
        margin-left: 10px;
        margin-top: 5px;
    }

    .vertical-selects {
        display: block;
        width: 100%; /* Optional: to make the select elements full-width */
        height: auto;
        margin-bottom: 20px; /* Optional: add space between the selects */
        margin-right: 10px;
        margin-left: 10px;
        margin-top: 10px;
    }


    .horizontal-elements {
        display: flex;
        gap: 20px;
        padding-top: 10px;
        margin-bottom: 20px; /* Optional: add space between the selects */
        height: auto;
    }


</style>