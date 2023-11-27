document.addEventListener("DOMContentLoaded", (e) => {
    /*initialise socket*/
    const socket = io({autoConnect: false});

    /*get elements for HTML*/
    const startQueueBtn = document.querySelector('#start_queue');
    const activateQueueForm = document.querySelector('.activate_queue');
    const activated = document.querySelector('#activate');
    const activateQueue = document.querySelector('#activate_queue')
    const showQueueBtn = document.querySelector('.show_queue_form')
    const joinQueueForm = document.querySelector('.join_queue_form')
    const submitJoinQueueForm = document.querySelector('#submit_join_queue_form')
    const organization = document.querySelector('.organizations')

    /*function to remove hidden class from form to reenter username */
    function displayActivateQueueForm(e) {
        console.log(e)
        e.preventDefault()
        activateQueueForm.classList.remove("hidden")
    }

    function displayCustomerJoinQueueForm() {
        joinQueueForm.classList.remove("hidden")
    }

    function connectOrgToSocket(e) {
        e.preventDefault()
        /*get username and queuename from form */
        let checked = document.getElementById('activate').value;
        console.log(checked)

        /*Connect to socket if activated*/
        if (checked) {
            socket.connect();
        }
        
    }

    function connectCustomerToSocket(e) {
        e.preventDefault()
        
        let firstName = document.getElementById('first_name').value;
        let lastName = document.getElementById('last_name').value;
        let email = document.getElementById('email').value;
        let contactNumber = document.getElementById('contact_number').value;
        let organization = document.querySelector('.organization_name').value;
        
        console.log('a')
        console.log(socket.connected)
        socket.connect()

        socket.on("connect", function() {
            socket.emit("add_unauth_to_queue", firstName, lastName, email, contactNumber, 'winners')
        })
    }

    /*check is the organization homepage is loaded  */
    if (startQueueBtn) {
        startQueueBtn.addEventListener('click', displayActivateQueueForm)
    }
    
    /*connect organization to socket*/
    if (activateQueue) {
        activateQueue.addEventListener('click', connectOrgToSocket)
    }


    if (showQueueBtn) {
        showQueueBtn.addEventListener('click', displayCustomerJoinQueueForm)
    }

    if (submitJoinQueueForm) {
        submitJoinQueueForm.addEventListener('click', connectCustomerToSocket)
    }

    if (organization) {
        organization.addEventListener('click', function(e) {
            if (e.target.classList.contains("organization_name")) {
                displayCustomerJoinQueueForm()
            } 
        })
    }
})

