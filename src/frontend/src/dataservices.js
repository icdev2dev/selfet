import { writable } from 'svelte/store';

export const url = "http://localhost:5000"

export const auth = writable(
    localStorage.getItem("user")? JSON.parse(localStorage.getItem('user'))?.login : false
)

export const agents = writable([])



export const listPupils = writable([]);
export const selectedPupil = writable(); 

export const providers = writable([]);
export const models = writable([]);

export const reading_tutor = writable();



export async function loginValidation(user_id, password){

    let id = ""
    return {"login": true, "role": "user", "name": user_id, "id":id}



    const response = await fetch(url+ `/login_check`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            user_id: user_id,
            password: password,
        })
    })
    const json = await response.json();
    return json;
}


export async function get_agents() {
    const response = await fetch(url+ `/agents`);

    if (response.ok) {
        const data = await response.json()
        
        agents.set(data)
        console.log(agents)
    } else {
        agents.set(['Error Fetching Data'])
    }
}

export async function get_agent_details(agent_name) {
    const response = await fetch(url+ `/agent_details/`+agent_name);
    

    if (response.ok) {
        const data = await response.json()
        
        return data
    } else {
        return 
    }

}

















export async function fetchAllData() {
        await get_agents()
        
    //    await get_models()
        
    //    await fetchPupils()
    //    await get_reading_tutor()
    
        
    }
    

async function get_reading_tutor() {
    const response = await fetch(url+ `/get_reading_tutor`);
    if (response.ok) {
        const data = await response.json()
        reading_tutor.set(data)
    } else {
        reading_tutor.set(['Error Fetching Data'])
    }
}


async function get_providers() {
    const response = await fetch(url+ `/get_providers`);
    if (response.ok) {
        const data = await response.json()
        providers.set(data)
    } else {
        providers.set(['Error Fetching Data'])
    }
}

async function get_models() {
    const response = await fetch(url+ `/get_models`);
    if (response.ok) {
        const data = await response.json()
        models.set(data)
    } else {
        models.set(['Error Fetching Data'])
    }
}

async function fetchPupils() {
    const response = await fetch(url+ `/list_pupils`);
    if (response.ok) {
        const data = await response.json();
        listPupils.set(data)
    } else {
        listPupils.set(['Error fetching data']);
    }
}


export async function deletePupil(pupil_id) {

    const response = await fetch(url+ `/delete_pupil/` +pupil_id, {
        method: 'DELETE',
    });

    if (response.ok) {
        const data = await response.json();
    } else {
    }
    
}

export async function createPupil(pupil_name, pupil_password, pupil_role) {

     const response = await fetch(url+ `/create_pupil/` +pupil_name, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            pupil_password: pupil_password,
            pupil_role: pupil_role
        })

     });

     if (response.ok) {
         const data = await response.json();
     } else {

    }    
 }


 

export async function createPupilRun(pupil_id, assistant_id) {

    const response = await fetch(url+ `/create_pupil_run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            pupil_id: pupil_id,
            assistant_id: assistant_id,
        })
    })

    if (response.ok) {
        const data = await response.json()
        return "ok"
    } else {
        return ('Error Fetching Data')
    }
        

}


 
export async function createPupilMessage(pupil_id, content1) {

    const response = await fetch(url+ `/create_pupil_message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            pupil_id: pupil_id,
            content: content1,
        })
    })

    if (response.ok) {
        const data = await response.json()
        return "ok"
    } else {
        return ('Error Fetching Data')
    }
    
    
}
 export async function getPupilMessages(pupil_id,  order = 'desc', limit = 100) {

    const response = await fetch(url+ `/get_pupil_messages`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            pupil_id: pupil_id,
            order: order,
            limit: limit
        })
    })

    if (response.ok) {
        const data = await response.json()
        return data
    } else {
        return (['Error Fetching Data'])
    }
 }
export async function getPupil(pupil_id) {
    const response = await fetch(url+  `/get_pupil/` + pupil_id)

    if (response.ok) {
        const data = await response.json()
        return data        
    } else {
        return ("Error fetching data")
    }
}


export async function createReadingTutor(provider, real_model, instructions) {
    const response = await fetch(url+ `/create_reading_tutor`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            provider: provider,
            real_model: real_model,
            instructions: instructions
        })

    });

    if (response.ok) {
        const data = await response.json();
    } else {
    }


}

export async function updateReadingTutor(assistant_id, provider, real_model, instructions) {

    const response = await fetch(url+ `/update_reading_tutor`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            assistant_id: assistant_id,
            provider: provider,
            real_model: real_model,
            instructions: instructions
        })

    });

    if (response.ok) {
        const data = await response.json();
    } else {
    }

}


export async function refreshReadingTutor() {
    await get_reading_tutor()

}
export async function refreshPupils() {
    await fetchPupils()
}




export async function exportPupilMessages(pupil_id) {
    const response = await fetch(url+ `/export_pupil_messages/` + pupil_id);
    if (response.ok) {
        const data = await response.json()
        return data        
    } else {
        return ("Error fetching data")
    }
}

