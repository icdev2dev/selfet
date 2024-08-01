<script>
    import AgentList from "../components/agents/AgentList.svelte";
    import GroupConversations from "../components/convo/GroupConversations.svelte";
    import OneOnOneConversations from "../components/convo/OneOnOneConversations.svelte";
</script>

Home Page : To be changed     

<div class="container">

    <GroupConversations>

    </GroupConversations>
  
    <OneOnOneConversations>

    </OneOnOneConversations>
    <AgentList width="500px" isHoverable={true}>
        
    </AgentList>

</div>

<style>
    .container {
        display: flex;
        justify-content: space-between;
    }

</style>

