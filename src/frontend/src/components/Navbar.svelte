
<script>
    import { Link } from "svelte-routing";
    import Home from "../pages/Home.svelte";
    import ConversationsPage from "../pages/Conversations.svelte";
    import AgentsPage from "../pages/Agents.svelte";
    import BrainStormPage from "../pages/BrainStorm.svelte";   
    import Logout from "./logout.svelte";

    // The tabs MUST be in sync with PrivateGuard

    let tabs = [
        { name: 'Home', route: '/', component: Home, path: "/" },
        { name: 'Conversations', route: '/conversations', component: ConversationsPage, path: "/conversations"},
        { name: 'Agents', route: '/agents', component: AgentsPage, path: "/agents"},
        { name: 'Brainstorm', route: '/brainstorm', component: BrainStormPage, path: "/brainstorm"}


    ]


</script>

<div>
    <nav>
        <ul>
            {#each tabs as tab}
                <li><Link to={tab.route}>{tab.name}</Link></li>
            {/each}        
            <li><Logout /></li>
        </ul>
    </nav>
</div>

<style>
    @import './Navbar.css'
</style>
