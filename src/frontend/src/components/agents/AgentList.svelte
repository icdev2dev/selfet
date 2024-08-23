<script>

    import {agents, get_agent_details} from '../../dataservices'
    import Hoverable from '../Hoverable.svelte';

    export let width="500px"
    export let isHoverable=true


    let coveredHoverAgent = null
    let currentAgentDetails = null;

    async function fetchAgentDetails(name) {
      const details = await get_agent_details(name);
      return details
    }
   

    $: {
        if (coveredHoverAgent) {
            fetchAgentDetails(coveredHoverAgent).then(details => {currentAgentDetails = details})
        } else {
            currentAgentDetails = null
        }
    }
    

</script>

<div style="width: {width};">
    {#each $agents as agent}

    <Hoverable let:hovering={active}>
        <div class:active     on:mouseenter={() => coveredHoverAgent = agent.name} role="tooltip" on:mouseleave={() => coveredHoverAgent = null}>
            {#if active && isHoverable && currentAgentDetails}

                <table>
                    <tr>
                        <td>
                            { JSON.parse (JSON.stringify((currentAgentDetails))).instructions }
                        </td>
                    </tr>

                </table>
                        
            {:else}
            {agent.name}
            {/if}
        </div>
    </Hoverable>
    {/each}
</div>
<style>
    table, td {
  border: 1px solid gray;
}
</style>