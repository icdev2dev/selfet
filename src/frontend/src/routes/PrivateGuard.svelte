<script>

    import { auth } from "../dataservices";
    import { tick } from "svelte";

    import { Route, Router, Link, navigate } from "svelte-routing";
    import Home from "../pages/Home.svelte";
    import ConversationsPage from "../pages/Conversations.svelte";
    import AgentsPage from "../pages/Agents.svelte";
    import BrainStormPage from "../pages/BrainStorm.svelte";

    import Navbar from "../components/Navbar.svelte";


    $: userRole = (JSON.parse(localStorage.getItem('user')))?.role

    $: if (!$auth) {
        tick().then(() => navigate("/login", { replace: true }));
    }

// The tabs MUST be in sync with Navbar
    
    let tabs = [
        { name: 'Home', route: '/', component: Home, path: "/" },
        { name: 'Conversations', route: '/conversations', component: ConversationsPage, path: "/conversations"},
        { name: 'Agents', route: '/agents', component: AgentsPage, path: "/agents"},
        { name: 'Brainstorm', route: '/brainstorm', component: BrainStormPage, path: "/brainstorm"}
        
    ]

</script>

<div>

    {#if userRole === 'user'}
        <Navbar></Navbar>
    {/if}


    <!-- Redirect to Active Conversations when navigating to /conversations -->
    <Route path="/conversations" component={() => {
        navigate("/conversations/activeConversations");
        return null; // Return null since we're only redirecting
    }} />
    
    <Route path="/agents" component={() => {
        navigate("/agents/creatorAgents");
        return null; // Return null since we're only redirecting
    }} />
    

    {#each tabs as tab}
        <Route path={tab.path} component={tab.component}></Route>
    {/each}



    <Route path="/conversations/*" component={ConversationsPage} />
    <Route path="/agents/*" component={AgentsPage} />
    <Route path="/brainstorm" component={BrainStormPage} />

</div>


