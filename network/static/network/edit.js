document.addEventListener('DOMContentLoaded', function() {
    
    // Use buttons to toggle between views
    //document.querySelector('#edit').addEventListener('click', () => edit_post(item_id));

});

function edit_post(id) {
    // Hide the edit button and clear out the post region
    document.querySelector(`#edit_${id}`).style.visibility = "hidden";
    document.querySelector(`#post_${id}`).innerHTML = "";
    
    // Build up the post_area components one by one
    let update = document.createElement('div');
    update.innerHTML = `<textarea id = "text_${id}" placeholder="Edit Post"></textarea>`
    document.querySelector(`#post_${id}`).append(update);

    let save = document.createElement('button');
    save.classList.add('btn');
    save.classList.add('btn-sm');
    save.classList.add('btn-outline-primary');
    save.innerText = 'Save';
    document.querySelector(`#post_${id}`).append(save);
    
    save.addEventListener("click", () => {
        //console.log("You have clicked on Save.");
        //console.log(document.querySelector(`#text_${id}`).value);
        let content = document.querySelector(`#text_${id}`).value;
        
        fetch('/update', {
            method: 'POST',
            body: JSON.stringify({
                post_id: id,
                submission: content
            })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result);
        });
        
        // Unhide the edit button and replace the post region
        document.querySelector(`#edit_${id}`).style.visibility = "visible";
        document.querySelector(`#post_${id}`).innerHTML = content;
    });
}


function increase_likes(id) {
    // Communicate with the appreciate function to add user to the like listing
    fetch('/appreciate', {
        method: 'POST',
        body: JSON.stringify({
            post_id: id
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        //console.log(result);
        
        // Refresh the quantity of likes on the page
        document.querySelector(`#like_amount_${id}`).innerHTML = result;
        
        // Update button
        document.querySelector(`#like_${id}`).innerHTML = "Unlike";
        document.querySelector(`#like_${id}`).setAttribute("onclick", `decrease_likes(${id})`);
    });
}


function decrease_likes(id) {
    // Communicate with the depreciate function to remove user from the like listing
    fetch('/depreciate', {
        method: 'POST',
        body: JSON.stringify({
            post_id: id
        })
    })
    .then(response => response.json())
    .then(result => {
        // Print result
        //console.log(result);
        
        // Refresh the quantity of likes on the page
        document.querySelector(`#like_amount_${id}`).innerHTML = result;
        
        // Update button
        document.querySelector(`#like_${id}`).innerHTML = "Like";
        document.querySelector(`#like_${id}`).setAttribute("onclick", `increase_likes(${id})`);
    });
}



