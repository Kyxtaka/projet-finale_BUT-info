
class Room {
    id;
    name;
    description;
    constructor(name, description, id) {
        this.id = `room-${id}`;
        this.name = name;
        this.description = description;
    }

    toString() {
        console.log(this.name, this.description);
        return this.name + " " + this.description;
    }
}


document.addEventListener("DOMContentLoaded", function() {
    const { BehaviorSubject } = rxjs; // import de rxjs apres avoir load le script dans le html car on utilise pas node et Typescript

    let elementId = 0;
    const arrayRooms = new BehaviorSubject([]);
    const $arryRooms = arrayRooms.asObservable();

    const logementForm = document.getElementById("add-logement-form");
    const formRoomsArray = document.getElementById("form-rooms-array");
    logementForm.addEventListener("submit", function(event) {
        event.preventDefault();
        console.log("arrayRooms JSON", JSON.stringify(arrayRooms.getValue()));
        document.getElementById("rooms-array").value = JSON.stringify(arrayRooms.getValue());
        console.log("form submitted");
        logementForm.submit();
    });

    const roomFormButton = document.getElementById('add-room-btn');
    const roomTable = document.getElementById('room-list');

    roomFormButton.addEventListener("click", function(event) {
        console.log("button clicked");

        event.preventDefault();
        let roomName = document.getElementById('edit-room-name-input').value;
        let roomDescription = document.getElementById('edit-room-description-input').value;

        console.log("roomName", roomName);
        console.log("roomDescription", roomDescription);


        let room = new Room(roomName, roomDescription, elementId);
        elementId++;

        arrayRooms.next([...arrayRooms.getValue(), room]);
        console.log("Updated rooms array:", arrayRooms.getValue());

        toggleFormPopup('add-piece-popup-form');
    });

    $arryRooms.subscribe({
        next: (response) => {
            console.log("arrayRooms Changed", arrayRooms.getValue());
            if (response.length > getHtmlTableLenght("room-list")) {
                console.log("rooms", response);
                let row = document.createElement('tr');
                row.id = `${response[response.length - 1].description}`;
                let nameCell = document.createElement('td');
                let descriptionCell = document.createElement('td');
                let actionCell = document.createElement('td');
                let actionButtonRemove = document.createElement('button');
                actionButtonRemove.id = `remove-${response[response.length - 1].id}`;
                actionButtonRemove.textContent = "Remove";
                actionButtonRemove.onclick = function() {removeRoom(response[response.length - 1].id);};

                // actionCell.appendChild(actionButtonRemove);
                actionCell.appendChild(actionButtonRemove);
                nameCell.textContent = response[response.length - 1].name;
                descriptionCell.textContent = response[response.length - 1].description;

                row.appendChild(nameCell);
                row.appendChild(descriptionCell);
                row.appendChild(actionCell);
                roomTable.appendChild(row);
            }
              
        },
        error: (error) => {
            console.error(error);
        },
    });

    function removeRoom(id) {
        console.log("removing room from array");
        const updatedRooms = arrayRooms.getValue().filter(room => room.id !== id);
        arrayRooms.next(updatedRooms);
         
        roomTable.deleteRow(`room-${id}`);
        setTimeout(() => {}, 5000);
        console.log("current array:", arrayRooms.getValue());
    }
    
    function getHtmlTableLenght(tableId) {
        table = document.getElementById(tableId);
        return table.rows.length;
    }

   function getArrayRooms() {
        return arrayRooms.getValue();
    }   

    //attribution d'action pour l element arrayValue qui appelle get getArrayRooms ONLY FOR DEBUG
    document.getElementById("arrayValue").addEventListener("click", function() {
        console.log(getArrayRooms());
    });

});

function toggleFormPopup(overlay_id) {
    console.log("overlay_id form", overlay_id);
    const overlay = document.getElementById(overlay_id);
    console.log("overlay", overlay);
    overlay.classList.toggle('show');
    for (i = 0; i < document.getElementsByClassName('action-btn').length; i++) {
        document.getElementsByClassName('action-btn')[i].style.display =  document.getElementsByClassName('action-btn')[i].style.display === 'none' ? 'block' : 'none';
    }
}
