<script>

    let user_id = '';
    let password = '';

    import {loginValidation} from "../dataservices";
    import {  navigate } from "svelte-routing";

    async function handleSubmit(event) {
      event.preventDefault();

      const res = await loginValidation(user_id, password)
      localStorage.setItem('user', JSON.stringify(res))
      const role = res?.role;

      if (res?.login){
        window.location.href = '/'
      } else{
        alert("Login Failed - Incorrect Username or Password")
      }
    }

</script>

<main>
    <h1>Login Page</h1>
    <form on:submit={handleSubmit}>
        <div>
          <label for="user_id">Username:</label>
          <input type="text" id="user_id" bind:value={user_id} required>
        </div>
        <div>
          <label for="password">Password:</label>
          <input type="password" id="password" bind:value={password} required>
        </div>

        <button type= "submit"  >Submit</button>
    </form>
  
</main>

<style>
    @import './login.css'
</style>
