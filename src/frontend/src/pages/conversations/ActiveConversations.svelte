
<script>

    import {activeConversations, getConversation} from "../../dataservices"
    import { marked } from "marked";
    let selectedConversationId
    let selectedConversation = null

    let isLoading = false
    let error = null;


    // Function to fetch conversation details using getConversation
    async function fetchConversationDetails(id) {
        isLoading = true;
        try {
            selectedConversation = await getConversation(id);
            if (typeof selectedConversation === 'string' && selectedConversation.startsWith('Error')) {
                error = selectedConversation;
                selectedConversation = null;
            }
        } catch (err) {
            error = "An error occurred while fetching the conversation details.";
            selectedConversation = null;
        } finally {
            isLoading = false;
        }
    }

    function displayMessage(message) {
        return marked(message)
    }




    $: if (selectedConversationId) {
        fetchConversationDetails(selectedConversationId);
    }


</script>



<!-- Container for the entire component -->
<div class="container">
    <!-- Selection div -->
    <div class="selection">
        <h4>Select a Conversation</h4>
        {#each $activeConversations as conversation}
            <div>
                <input 
                    type="radio" 
                    id={conversation.id} 
                    name="conversation" 
                    value={conversation.id}
                    bind:group={selectedConversationId} 
                />
                <label for={conversation.id}>{conversation.name}</label>
            </div>
        {/each}
    </div>



        <!-- Details div -->
    <div class="details">
            {#if isLoading}
                <p>Loading conversation details...</p>
            {:else if error}
                <p>{error}</p>
            {:else if selectedConversation}
                <h2>Conversation Details</h2>

                <table>
                    <tr>
                        <th> Name </th>
                        <th> Maximum Number of Allowed Messages </th>
                        <th> Number of Actual Messages </th>
                    </tr>
                    <tr>
                        <td> {selectedConversation.conversation_name} </td>
                        <td> {selectedConversation.max_msgs_on_thread} </td>
                        <td> {selectedConversation.num_of_msgs_on_thread} ({selectedConversation.msgs_by_author}) </td>
                    </tr>
                </table>
                {#if selectedConversation.msgs.length > 0}
                        {#each selectedConversation.msgs as message}
                            <div class="user-message">
                                {@html displayMessage(message.text)}
                            </div>
                        {/each}
                {:else}
                    <p>No messages available.</p>
                {/if}

            {:else}
                <p>Select a conversation to see details.</p>
            {/if}
    </div>



</div>

<style>

    .container {
        display: flex;
        height: 100vh; /* Optional: makes the container full height */
        width: 100%;   /* Ensures the container takes full width */
    }

    .selection {
        flex: 0 0 20%; /* Fixed width of 20% */
        padding: 10px;
        align-self: flex-start;
        text-align: left;
        border-right: 1px solid #ccc; /* Optional: add a border between the two sections */
        box-sizing: border-box; /* Ensures padding and border are included in the width */
    }

    .details {
        flex: 1; /* Takes up the remaining space (80%) */
        padding: 10px;
        box-sizing: border-box; /* Ensures padding is included in the width */
    }

    .user-message{
        background-color: #4f8df5;
        color: hwb(0 95% 4%);
        align-self: flex-start;
        text-align: left;
        border: #989191;
        
        padding: 20px;
        border-radius: 15px 15px 15px 15px;
        margin-bottom: 10px;
    }



    table {
        width: 100%;
        border-collapse: collapse; /* Ensures borders are collapsed into a single border */
    }

    th, td {
        border: 1px solid #ddd; /* Light gray border for table cells */
        padding: 8px; /* Adds padding inside cells */
        text-align: left; /* Aligns text to the left */
    }

    th {
        background-color: #989191; /* Light gray background for header cells */
        font-weight: bold; /* Makes header text bold */
    }

    tr:nth-child(even) {
        background-color: hsl(0, 1%, 26%); /* Zebra striping for rows */
    }

    tr:hover {
        background-color: hsl(0, 2%, 27%); /* Highlight row on hover */
    }
</style>
