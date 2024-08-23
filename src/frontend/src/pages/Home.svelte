<script>
    import AgentList from "../components/agents/AgentList.svelte";
    import { getActiveConversations, getConversation, setConversationType } from "../dataservices";
    import socketStore from "../stores/socket";
    import { marked } from "marked";
    import { onMount } from "svelte";
    import {activeConversations, agents} from "../dataservices"

    let isLoading = false
    let confirmationMessage = ""

    let error = null;


    let buttonHeight = '40px';
    let buttonWidth = '150px';

    let textmsg
    let socket

    let selectedAgent = '';
    let selectedConversation
    let selectedConversationId
    let selectedOption = "MMA"; // Default radio option
    let selectedDropdownOption = "";

    const options = {
        "MMA": [],
        "SAMA": ["Unrestricted", "Balanced", "RoundRobin"],
        "AMA": ["Balanced", "RoundRobin"],
    };

    $: additionalOptions = options[selectedOption];


    async function handleConversationTypeChange(newType) {
        console.log("Selected Thread Id:", selectedConversationId);

        console.log("Selected Conversation Type:", newType);
        let response
        confirmationMessage = '';

        if (selectedConversationId != null) {


            // You can perform any action based on the selected type here
            // For example, update additional options, fetch data, etc.
            try {
                isLoading = true
                response = await setConversationType(selectedConversationId, newType)
                isLoading = false

            } catch (err) {

                isLoading = false
                confirmationMessage = 'failed!'
                
            }
        }

    }

    // This will be triggered automatically by Svelte whenever `selectedOption` changes
    $: handleConversationTypeChange(selectedOption);

    function displayMessage(message) {
        return marked(message)
    }



    onMount(() => {
        triggerSelect()
    });

    async function triggerSelect() {
        selectedConversationId = null
    }

    async function clicked_post_message() {

        try {

            isLoading = true;
            confirmationMessage = '';

            socket.emit("request_response", {
                                             realRequest: 'post_request',
                                             realRequestData: textmsg.value, 
                                             originator: selectedAgent, 
                                             destination_thread_id: selectedConversationId, 
                                             respondAt: 'updatePostRequest' 
                                            });
            
            // Listen for the specific response from the server
            socket.on('updatePostRequest', (response) => {
                // Handle response, hide hourglass, and show confirmation message
                isLoading = false;

                if (response.status === 'success') {
                    confirmationMessage = 'Post was successful!';
                } else {
                    confirmationMessage = 'Post failed: ' + response.error;
                }
            });


            
        } catch(error) {
            
            isLoading = false;
            confirmationMessage = 'An error occurred: ' + error.message;
        }
    }

    function handleSelectedAgentChange(event) {
        selectedAgent = event.target.value
    }

    async function handleSelectedConversationChange(event) {
        selectedConversationId = event.target.value
        console.log(selectedConversationId)

        if (selectedConversationId != null) {
            try {
                selectedConversation = await getConversation(selectedConversationId)
                console.log(selectedConversation.conversation_name)
                console.log(selectedConversation.conversation_type)
                selectedOption = selectedConversation.conversation_type

                console.log(typeof selectedConversation)

            } catch(err) {
                console.log("some error")       
            }

        }

    }

    socketStore.subscribe(value => {
        socket = value;
    })

    $: if (socket) {
        let response


        socket.on('newMessageAdded', async(data) => {
            console.log("New Message has been added !")
            try {
                selectedConversation = await getConversation(selectedConversationId)
            } catch(err) {
            
            }


        })
        socket.on('madeConversationInactive', async(data) => {
            
            try {
                response = await getActiveConversations()

            }
            catch (err){

            }
        })
    }
</script>

<div>
    <div class="container">
        <div class="vertical-selects">
            <div class="horizontal-elements">
                Agent
                <select bind:value={selectedAgent} on:change={handleSelectedAgentChange}>
                    {#each $agents as agent}
                        <option value={agent.name}>{agent.name}</option>
                    {/each}
                </select>
            </div>

            <div class="horizontal-elements">
                Conversation
                <select bind:value={selectedConversationId} on:change={handleSelectedConversationChange}>
                    {#each $activeConversations as conversation}
                        <option value={conversation.id}>{conversation.name}</option>
                    {/each}
                </select>
            </div>
        </div>
        <textarea bind:this={textmsg} style="width: 500px"> </textarea>

        <div class="vertical-selects">
            <div class="horizontal-elements">

                <button class="button-post"  on:click={clicked_post_message}> Post Message </button>
                {#if isLoading}
                    <div class="hourglass">⏳ Loading...</div>
                {/if}

        <!-- Show confirmation message when available -->
                {#if confirmationMessage}
                    <div class="confirmation">{confirmationMessage}</div>
                {/if}
            </div>
    <!-- Radio selection for agent mode -->
            <div class="horizontal-elements">

                <div class="vertical-selects-with-borders">
                    Conversation Type

                    <div class="radio-group">
                        <label class="tooltip-label" title="Manual MultiAgents: User manually selects agents to respond">
                            <input type="radio" value="MMA" bind:group={selectedOption}>
                            MMA
                        </label>
                        <label class="tooltip-label" title="Semi-Autonomous MultiAgents: Agents partially controlled by the user">
                            <input type="radio" value="SAMA" bind:group={selectedOption}>
                            SAMA
                        </label>
                        <label class="tooltip-label" title="Autonomous MultiAgents: Agents fully autonomous">
                            <input type="radio" value="AMA" bind:group={selectedOption}>
                            AMA
                        </label>
                    </div>

                    <div>

                        <label for="additionalOptions">Additional Options</label>
                        <select id="additionalOptions">
                            {#each additionalOptions as option}
                                <option value={option}>{option}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <div >
            <p class="with-borders"> Agents</p>

            <div class="with-borders"> 
                <AgentList  isHoverable={true}>            
                </AgentList>
            </div>
        </div>
    </div>

    <div class="container-user">
        <div class="welcome-message">
                <div>
                    <p>👋 Hi there! Welcome to Selfet ! 📚😊Just use the interface above as a conversation starter or to steer an ongoing conversation. 📖✨</p>
                </div>
        </div>
    </div>

    <div class="container">

        <div class="details">
            {#if isLoading}
                <p>Loading conversation details...</p>
            {:else if error}
                <p>{error}</p>
            {:else if typeof selectedConversation === 'object' }
                <h2>Conversation Details ( {selectedConversation.conversation_name} ) </h2>
                
                {#if typeof selectedConversation.msgs === 'undefined'}
                    <p>1..No messages available.</p>
                {:else}
                    {#if selectedConversation.msgs.length > 0}
                            {#each selectedConversation.msgs as message}
                                <div class="user-message">
                                    {@html displayMessage(message.text)}
                                </div>
                            {/each}
                    {:else}
                        <p>No messages available.</p>
                    {/if}

                {/if}


            {:else}
                <p>Select a conversation to see details.</p>
            {/if}
    </div>

    </div>






</div>



<style>
    .with-borders {
        border: hwb(0 59% 39%);
        width: 100%;
    }
    .button-post {
        background-color: #4f8df5;

    }
    .radio-group label {
        margin-right: 20px;
        cursor: pointer;
        font-size: 12px; /* Increase the font size */
    }

    .radio-group label:hover {
        font-size: 14px; /* Increase font size on hover */
        font-weight: bold; /* Optionally, make the text bold on hover */
    }
    .container {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        border-spacing: 1cm;
    }
    .vertical-selects select {
        display: block;
        width: 100%; /* Optional: to make the select elements full-width */
        margin-bottom: 10px; /* Optional: add space between the selects */
        margin-right: 10px;
    }

    .vertical-selects-with-borders select {
        display: block;
        width: 100%; /* Optional: to make the select elements full-width */
        margin-bottom: 10px; /* Optional: add space between the selects */
        margin-right: 10px;
        border: hsl(0, 14%, 92%);
    }

    .horizontal-elements {
        display: flex;
        gap: 20px;
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
    .hourglass {
        font-size: 20px;
        color: #999;
    }

    .confirmation {
        margin-top: 5px;
        height: 30px;
        width: 150px;
        padding: 5px;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
</style>

