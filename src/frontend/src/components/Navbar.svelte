
<script>
    import { Link } from "svelte-routing";
    import Home from "../pages/Home.svelte";
    import AddedHome from "../pages/AddedHome.svelte";
    import Logout from "./logout.svelte";

    // The tabs MUST be in sync with PrivateGuard

    let tabs = [
        { name: 'Home', route: '/', component: Home, path: "/" },
        { name: 'AddedHome', route: '/addedhome', component: AddedHome, path: "/addedhome" }
    ];


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
