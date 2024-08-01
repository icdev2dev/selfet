<!-- Logout.svelte -->
<script>
    
    function handleLogout() {
       localStorage.clear();
       window.location.href = '/login'; // Use this if navigate doesn't work
    }
</script>
  
  
  <button class="logout-button" on:click={handleLogout}>Logout</button>
  
  <style>
    @import './logout.css'
  </style>
  