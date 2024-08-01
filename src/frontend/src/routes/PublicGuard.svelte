<script>
    import { Router, Route } from "svelte-routing";
    import LoginPage from "../components/login.svelte";
    
</script>

<Router>
    <Route  path="/login" component={LoginPage} />
</Router>

