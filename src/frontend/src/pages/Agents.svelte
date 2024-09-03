<script>

    import { Router, Route, Link, navigate } from "svelte-routing";
    import CreateAgentPage from "./agents/CreateAgent.svelte";
    import CreatorAgentsPage from "./agents/CreatorAgents.svelte";
    import ReviewerAgentsPage from "./agents/ReviewerAgents.svelte";

    let tabs = [
        {name:'Creator Agents', route: 'creatorAgents', component: CreatorAgentsPage},
        {name:'Reviewer Agents', route: 'reviewerAgents', component: ReviewerAgentsPage},
        {name:'Create New Agent', route: 'createAgent/*', component: CreateAgentPage},
    ]

</script>

<Router>    
    
    <div class="container">
        <div class="sidebar">
            <ul>
                {#each tabs as tab}
                    <li>
                        <Link to={tab.route}>{tab.name}</Link>
                    </li>
                {/each}

            </ul>
        </div>
     
    
        <div class="main-content">
            {#each tabs as tab}
                <Route path={tab.route} component={tab.component} />
            {/each}
        </div>
    </div>
</Router>

<style>


    .container {
        display: flex;
        flex-direction: row; /* Horizontal layout by default */
        width: 100%;
    }
  
    .sidebar {
        width: 15%;
        padding: 10px;
    }
  
    .sidebar ul {
        list-style-type: none; /* Removes bullet points */
        padding-left: 0; /* Removes padding on the left */
        margin: 0; /* Removes default margin */
    }

    .sidebar li {
        padding: 8px; /* Adds padding to each list item for spacing */
        margin-bottom: 5px; /* Adds space between list items */
        border-bottom: 1px solid #ccc; /* Optional: adds a subtle line between items */
    }

    .main-content {
      width: 90%;
      padding: 10px;
    }
  
</style>
