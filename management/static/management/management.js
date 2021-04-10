document.addEventListener('DOMContentLoaded', function() {

    // Gives the ability to mark a maintenance request as resolved/unresolved
    document.querySelectorAll('.resolve').forEach(b => {
        b.onclick = function() {
            // Request's unique id 
            const request_id = this.dataset.request

            fetch(`/resolve/${request_id}`)
            .then(() => {
                // If the request is unresolved, mark as resolved
                if (this.innerHTML === "Mark as resolved") {
                    title = document.querySelector(`#maintenance_title${request_id}`);
                    this.innerHTML = "Mark as unresolved";
                    title.innerHTML = "Resolved";
                    title.style.color = "green";
                } else {
                    // If the request is resolved, mark as unresolved
                    title = document.querySelector(`#maintenance_title${request_id}`);
                    this.innerHTML = "Mark as resolved";
                    title.innerHTML = "Unresolved";
                    title.style.color = "red";
                }
            });
        }
    });

    // Gives the ability to add a tenant to a property
    var el = document.querySelector('#add_tenant')
    if(el) {
        el.addEventListener("click",  () => {
            const b = document.querySelector('#add_tenant');
        
            // Create an empty form
            if (b.innerHTML === "Add a tenant") {
                var content = document.createElement("textarea");                
                content.className = 'form-control';
                document.body.appendChild(content);
                b.innerHTML = 'Submit';
            } else {
                console.log("test")
                console.log(b.parentElement.childNodes[21].value)
                var form = new FormData();
                form.append('email', b.parentElement.childNodes[21].value);
                form.append('unit_id', b.dataset.unit);
    
                // Submit the form via POST
                fetch("/add_tenant", {
                    method: 'POST',
                    body: form,
                })
                .then(() => {
                    document.querySelector('.form-control').style.display = 'none';
                    b.innerHTML = "Add a tenant";
    
                    // Append the email to the <li> of "People living in this property"
                    var email = document.createElement("li")
                    var content = document.createTextNode(b.parentElement.childNodes[21].value)
                    email.appendChild(content);
        
                    var person = document.getElementById("people")
                    person.appendChild(email);
                })
            }
        })

    }
})
