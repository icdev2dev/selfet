<script>
    // Declare variables for the form inputs

    import { navigate } from "svelte-routing";
    let name = '';
    let maxMessages = 5;

    import { createConversation, getActiveConversations, getInactiveConversations } from "../../dataservices";

    // Function to handle form submission
    async function handleSubmit(event) {
        event.preventDefault(); // Prevent default form submission behavior

        // You can handle the form data here
        console.log('Name:', name);
        console.log('Max Messages:', maxMessages);
        const response = await createConversation(name, maxMessages)

        if (response == "ok") {
            console.log("ok")

            getActiveConversations()
            getInactiveConversations()
            
            navigate("/conversations")

        }


        // Additional logic for form submission (e.g., API call, etc.)
    }
</script>

<!-- Form Structure -->
<form on:submit={handleSubmit}>
    <!-- Name Input -->
    <div>
        <label for="name">Conversation Name</label>
        <input type="text" id="name" bind:value={name} placeholder="Enter conversation name" />
    </div>

    <!-- Max Messages Input -->
    <div>
        <label for="maxMessages">Max Messages</label>
        <input type="number" id="maxMessages" bind:value={maxMessages} min="0" placeholder="Enter max messages" />
    </div>

    <!-- Create Button -->
    <button type="submit">Create</button>
</form>



<style>
    form {
        max-width: 300px;
        margin: auto;
        padding: 1rem;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    div {
        margin-bottom: 1rem;
    }

    label {
        display: block;
        margin-bottom: 0.5rem;
    }

    input {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    button {
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        background-color: #007BFF;
        color: white;
        cursor: pointer;
    }

    button:hover {
        background-color: #0056b3;
    }
</style>
