<!-- Logout.svelte -->
<script>
  let buttonHeight = '30px';
  let buttonWidth = '90px';

    function handleLogout() {
       localStorage.clear();
       window.location.href = '/login'; // Use this if navigate doesn't work
    }
</script>
  
  
  <button style:height={buttonHeight} style:width={buttonWidth} class="logout-button" on:click={handleLogout}>Logout</button>
  
  <style>
    @import './logout.css'
  </style>
  