document.addEventListener("DOMContentLoaded", (e) => {
    /*initialise socket*/
    const socket = io({autoConnect: false});
    console.log(socket.connected)

    

    /*get elements for HTML*/
    const startQueueBtn = document.querySelector('#start_queue');
    const activateQueueForm = document.querySelector('.activate_queue');
    const activated = document.querySelector('#activate');
    const activateQueue = document.querySelector('#activate_queue');
    const showQueueBtn = document.querySelector('.show_queue_form');
    const joinQueueForm = document.querySelector('.join_queue_form');
    const submitJoinQueueForm = document.querySelector('#submit_join_queue_form');
    const organization = document.querySelector('.organizations');
    const getTravelTime = document.querySelector('.agree_btn');
    const customerCode = document.querySelector('.customer_code');
    const leaveWaitlistBtn = document.querySelector('.leave_waitlist');
    const confirmLeaveNotif = document.querySelector('.confirm_leave');
    const notificationsOrg = document.querySelector('.notifications')
    const modeOfTravelForm = document.querySelector('.mode-of-travel-form')
    const submitModeOfTravelForm = document.querySelector("#submit-mode-of-travel")
    const organizationNameInForm = document.querySelector(".organization-name-in-form")
    let organizationNameTag = document.querySelector('.organization-card-title')
    let phoneInput;
    

   
   let organizationName;

    /*function to remove hidden class from form to reenter username */
    function displayActivateQueueForm(e) {
        console.log('e')
        e.preventDefault()
        activateQueueForm.classList.remove("hidden")
    }

    function displayCustomerJoinQueueForm() {
        joinQueueForm.classList.remove("hidden")
    }

    function connectOrgToSocket(e) {
        //function to connect organization to socket to activate queue
        e.preventDefault()
        /*get username and queuename from form */
        let checked = document.getElementById('activate').value;
        console.log(checked)

        /*Connect to socket if activated*/
        if (checked) {
            socket.connect();

            socket.emit('join')
        }
    }

     function getCustomerLocation(e) {
        const getTravelTimeCard = document.querySelector('.get_travel_time_card')
        const travelTimeResponse = document.querySelector('.travel-time-response')
        const distanceSpan = document.querySelector('.distance')
        const timeSpan = document.querySelector('.time')

        e.preventDefault()
        console.log(e)

        travel_mode = document.querySelector('input[name="travel-mode"]:checked').value;
        console.log(e.target.classList)
        
        async function successCallback(position) {
            console.log(position.coords.latitude)

            const dataToSend = {
                'latitude': position.coords.latitude,
                'longitude': position.coords.longitude, 
                'travel_mode': travel_mode
            }

            

            const response = await axios.get(`/customer/${customerCode.textContent}/directions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend)
            })
            
            const distanceAndTime = await response.json()
           
            getTravelTimeCard.classList.add('hidden')
            travelTimeResponse.classList.remove('hidden')
            travelTimeResponse.classList.add('add_flex')

            distanceSpan.textContent = distanceAndTime.distance;
            timeSpan.textContent = distanceAndTime.time


        }

        const errorCallback = (error) => {
            console.log(error)
        }

        console.log(customerCode.textContent)

        navigator.geolocation.getCurrentPosition(successCallback, errorCallback, {
            enableHighAccuracy: true
        })
    }

    function showModeOfTravelRequest(e) {
        e.preventDefault(e);
        modeOfTravelForm.classList.remove("hidden")
    }

    function showLeaveWaitlistNotif(e) {
        e.preventDefault()
        confirmLeaveNotif.classList.remove("hidden")
    }

    /*intl phone number validation*/
    

    /*check is the organization homepage is loaded  */
    if (startQueueBtn) {
        startQueueBtn.addEventListener('click', displayActivateQueueForm)
    }
    
    /*connect organization to socket*/
    if (activateQueue) {
        activateQueue.addEventListener('click', connectOrgToSocket)
    }

    //show form for customer to join
    if (showQueueBtn) {
        showQueueBtn.addEventListener('click', displayCustomerJoinQueueForm)
    }
    
    if (getTravelTime) {
        getTravelTime.addEventListener('click', showModeOfTravelRequest)
    }

    if (submitModeOfTravelForm) {
        submitModeOfTravelForm.addEventListener('click', getCustomerLocation)}
    
    if (leaveWaitlistBtn) {
        leaveWaitlistBtn.addEventListener('click', showLeaveWaitlistNotif)
    }




    //check if password or email is same as confirm password or email 
    const password = document.querySelector("#password")
    const confirmPassword = document.querySelector("#password_confirm")
    const message = document.querySelector("#message")

    const email = document.querySelector("#email-address")
    const confirmEmail = document.querySelector("#email-address-confirm")

    if (password && confirmPassword) {
        confirmPassword.addEventListener("keyup", passConfirm)
    }

    if (email && confirmEmail) {
        confirmEmail.addEventListener("keyup", emailConfirm)
    }

    function passConfirm(e) {
        e.preventDefault();
        if (password.value == confirmPassword.value) {
            message.style.color = "Green"
            message.textContent = "Passwords Match"
        } else {
            message.style.color = "Red"
            message.textContent = "Passwords do not match"
        }
    }

    function emailConfirm(e) {
        e.preventDefault();
        if (email.value == confirmEmail.value) {
            message.style.color = "Green"
            message.textContent = "Email addresses match"
        } else {
            message.style.color = "Red"
            message.textContent = "Email addresses do not match"
        }
    }

    /*hiding and displaying join queue forms*/
    const queueForm = document.querySelector(".join-queue-form")
    const groupSize = document.querySelector(".group-size")
    const individualOrGroupForm = document.querySelector(".individual_or_group")
    const allQueues = document.querySelector(".all-queues")

    const showCustomerInfoForm = e => {
        console.log(e)
        e.preventDefault();
        customer_size = document.querySelector('input[name="customer-size"]:checked').value;
        console.log(customer_size)
        individualOrGroupForm.classList.add("hidden");

        /*show queue form*/
        queueForm.classList.remove("hidden")
        queueForm.classList.add("show_queue_form")
        if (customer_size == 'group') {
            groupSize.classList.remove("hidden")
        }

        const phoneInputField = document.querySelector("#phone");

        console.log(phoneInputField)
        
        if (phoneInputField) {
            phoneInput = window.intlTelInput(phoneInputField, {
            utilsScript:
            "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
            });
       } 
    }
    
    //get organization name that customer wants to join queue
    if (organization) {
        organization.addEventListener('click', function(e) {
            organizationName = e.target.parentElement.children[0].innerText
            allQueues.classList.add('hidden')
            individualOrGroupForm.classList.remove('hidden')
            e.preventDefault()
        })
    }

    individualOrGroupForm ? individualOrGroupForm.addEventListener('submit', showCustomerInfoForm) : null

    function connectCustomerToSocket(e) {
        //function to connect customer to socket to join queue


        console.log(e)
        e.preventDefault()

        console.log(organizationName)
       
        /*get form data*/
        let firstName = document.getElementById('first_name').value;
        let lastName = document.getElementById('last_name').value;
        let email = document.getElementById('email').value;
        let contactNumber = phoneInput.getNumber();
        let groupSize = document.getElementById('group_size').value || null;

        console.log(contactNumber)

        socket.connect()
        
        socket.emit('join_queue', {
            firstName:firstName,
            lastName:lastName,
            email:email,
            contactNumber:contactNumber,
            organizationName:organizationName,
            groupSize : groupSize
        })
        
        
        
    }

    //on redirect socket should take the customer to the queue page
    socket.on('redirect_customer', function(destination) {
        window.location.href = destination.url
    })

     //on redirect socket should take the organization to the queue page
     socket.on('refresh_organization', function(destination) {
        window.location.href = destination.url
    })


    //connect customer to socket when clicked on submit form
    if (submitJoinQueueForm) {
        submitJoinQueueForm.addEventListener('click', connectCustomerToSocket)
    }

    //on search for queues, hide the cards that are not being searched for 

    const orgWithQueueCard = document.querySelectorAll('.organization_with_queue')
    let organizationNames = []

    if (orgWithQueueCard) {
        /*get organization names from the DOM*/
        orgWithQueueCard.forEach(orgCard => {
            organizationNames.push(orgCard.children[0].innerText) 
        })
        console.log(organizationNames)
    }

    //get input bar
    const searchQueuesInput = document.querySelector('#search_queues')

    //filter through queue to get what is being searched
    const filterQueue = e => {
        e.preventDefault()
        
        let queuesForCustomer = organizationNames.filter(organizationName => {
            return organizationName.includes(searchQueuesInput.value)
        })

        console.log(queuesForCustomer)
        orgWithQueueCard.forEach(orgCard => { 
            if(!(queuesForCustomer.includes(orgCard.children[0].innerText)) && !(orgCard.classList.contains('hidden'))) {
                orgCard.classList.add('hidden')
            }
        })
    }

    searchQueuesInput? searchQueuesInput.addEventListener('keyup', filterQueue) : null

    //on click of profile, add underline to what is currently being shown
    const profileLink = document.querySelector('#profile-link')
    const securityLink = document.querySelector('#security-link')

    const toggleUnderline = e => {
        //toggle underline between profile and security
        let targetSpan = e.target.parentElement.children[1];
        targetSpan.classList.add('underline');

        if (targetSpan.innerText == 'Profile') {
            securityLink.children[1].classList.remove('underline')
        } else if (targetSpan.innerText == 'Security') {
            profileLink.children[1].classList.remove('underline')
        }

    }

    profileLink ? profileLink.addEventListener('click', toggleUnderline) : null
    securityLink ? securityLink.addEventListener('click', toggleUnderline) : null
    

})

