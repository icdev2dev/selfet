<script>
  import { Router } from "svelte-routing";
  import DataServices from "./DataServices.svelte";
  import PrivateGuard from "./routes/PrivateGuard.svelte";
  import PublicGuard from "./routes/PublicGuard.svelte";
</script>

<DataServices>
  
</DataServices>
<main>
  <div class="mainContent" style="flex: 1; min-height:0;">
    
    <Router>
      <PrivateGuard></PrivateGuard>      
      <PublicGuard />
    </Router>

  </div>
</main>


