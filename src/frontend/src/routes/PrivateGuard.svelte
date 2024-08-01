<script>

    import { auth } from "../dataservices";
    import { tick } from "svelte";

    import { Route, Router, Link, navigate } from "svelte-routing";
    import Home from "../pages/Home.svelte";
    import AddedHome from "../pages/AddedHome.svelte";
    import Navbar from "../components/Navbar.svelte";

    $: userRole = (JSON.parse(localStorage.getItem('user')))?.role

    $: if (!$auth) {
        tick().then(() => navigate("/login", { replace: true }));
    }

// The tabs MUST be in sync with Navbar
    
    let tabs = [
        { name: 'Home', route: '/', component: Home, path: "/" },
        { name: 'AddedHome', route: '/addedhome', component: AddedHome, path: "/addedhome"}
    ]

</script>

<div>

    {#if userRole === 'user'}
        <Navbar></Navbar>
    {/if}

    {#each tabs as tab}
        <Route path={tab.path} component={tab.component}></Route>
    {/each}
</div>


