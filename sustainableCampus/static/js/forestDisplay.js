//onClick events -------------------------------------------------------------------------------------

function onForestCellClick(cell) {
    let occupiedPopup = document.getElementById("occupied-popup");
    let emptyPopup = document.getElementById("empty-popup");

    emptyPopup.selectedCell = cell;
    if (cell.plantId == "0") { //if cell is empty
        if (occupiedPopup.style.display == "block") { closePopup(occupiedPopup); }  //closes other popup

        //opens popup to plant tree
        openPopup(emptyPopup);
    }
    else {
        if (emptyPopup.style.display == "block") { closePopup(emptyPopup); }
        //opens popup to view plant progress
        openPopup(occupiedPopup);
        let plantName = plantArray[cell.plantId][3];
        let plantRequirementType = plantArray[cell.plantId][1];
        //update popup details
        document.getElementById("plant-name").innerText = plantName;
        document.getElementById("selected-plant-image").src = cell.plantImagePath;
        document.getElementById("selected-plant-description").innerHTML = "Growth stage: " + cell.plantGrowthStage
        let resource = "";
        switch (plantRequirementType) {
            case "0":
                resource = "Water";
                break;
            case "1":
                resource = "Tree Guard";
                break;
            case "2":
                resource = "Fertiliser";
                break;
        }

        document.getElementById("selected-plant-resource").innerHTML = "Plant Requires: " + resource;
        const resourceButton = document.getElementById("selected-plant-requirement-button");
        if (cell.plantRequirement == 1) {
            resourceButton.innerHTML = "Give " + resource;
            resourceButton.disabled = false;
        }
        else {
            resourceButton.innerHTML = "Plant seems happy!";
            resourceButton.disabled = true;
        }
    }
}

function onCustomiseClick() {
    let customisePopup = document.getElementById("customise-popup");
    let sellPopup = document.getElementById("sell-popup");
    if (customisePopup.style.display == "block") {
        closePopup(customisePopup)
    }
    else {
        if (sellPopup.style.display == "block") {
            closePopup(sellPopup);
        }
        openPopup(customisePopup);
    }
}

function onSellClick() {
    let customisePopup = document.getElementById("customise-popup");
    let sellPopup = document.getElementById("sell-popup");
    if (sellPopup.style.display == "block") {
        closePopup(sellPopup)
    }
    else {
        if (customisePopup.style.display == "block") {
            closePopup(customisePopup);
        }
        openPopup(sellPopup);
    }
}

function onRecyclingClick() {
    let recyclingPopup = document.getElementById("recycling-popup");
    if (recyclingPopup.style.display == "block") {
        recyclingPopup.style.animation = "recycling-exit 0.5s";
        setTimeout(function () { recyclingPopup.style.display = "none"; }, 480);
    }
    else {
        let occupiedPopup = document.getElementById("occupied-popup");
        let emptyPopup = document.getElementById("empty-popup");
        let customisePopup = document.getElementById("customise-popup");
        let sellPopup = document.getElementById("sell-popup");
        if (occupiedPopup.style.display == "block") {
            closePopup(occupiedPopup)
        }
        if (emptyPopup.style.display == "block") {
            closePopup(emptyPopup)
        }
        if (customisePopup.style.display == "block") {
            closePopup(customisePopup)
        }
        if (sellPopup.style.display == "block") {
            closePopup(sellPopup)
        }
        recyclingPopup.style.display = "block";
        recyclingPopup.style.animation = "recycling-enter 0.5s";
    }
}

function onPlantCellClick(cell) {
    //disable button if no plants are in inventory
    let plantButton = document.getElementById("plant-selected-button");
    plantButton.selectedPlantId = cell.selectedPlantId;
    if (cell.selectedPlantCount == 0) {
        plantButton.disabled = true;
    }
    else {
        plantButton.disabled = false;
    }
    document.getElementById("selected-plant-name").innerHTML = cell.selectedPlantName;
    let resourceName = "";
    switch (cell.selectedPlantResource) {
        case "0":
            resourceName = "Water";
            break;
        case "1":
            resourceName = "Tree Guard";
            break;
        case "2":
            resourceName = "Fertiliser";
            break;
    }
    document.getElementById("selected-seed-resource").innerHTML = "Plant Resource: " + resourceName;
}

function onCustomiseCellClick(cell) {
    let selectedCustomisations = document.getElementById("retrieved-selected-customisation-content").innerHTML.split(",");
    //checks type of customisation and applies to appropriate area
    switch (cell.customisationType) {
        case "0":   //sky
            document.getElementById("forest-view").style.backgroundImage = "linear-gradient(" + cell.primaryColour + ", " + cell.secondaryColour + ")";
            selectedCustomisations[0] = cell.customisationId;
            break;
        case "1":   //ground
            document.getElementById("forest-floor-texture").style.backgroundColor = cell.primaryColour;
            document.getElementById("forest-background-left").style.backgroundColor = cell.secondaryColour;
            //brighten secondary colour for lighter side of column
            let colorValue = parseInt(cell.secondaryColour.slice(1), 16);           //remove # from start
            let adjustment = 40;                                                    //increase brightness by 40%
            let tertColor = "#" + (((colorValue & 0x0000FF) + adjustment) |
                ((((colorValue >> 8) & 0x00FF) + adjustment) << 8) |
                (((colorValue >> 16) + adjustment) << 16)).toString(16);
            document.getElementById("forest-background-right").style.backgroundColor = tertColor;
            selectedCustomisations[1] = cell.customisationId;
            break;
        case "2":   //grid
            let elements = document.getElementsByClassName("grid-item");
            console.log(elements);
            for (var i = 0; i < elements.length; i++) {
                elements[i].style.borderTopColor = cell.secondaryColour;
                elements[i].style.borderRightColor = cell.secondaryColour;
                elements[i].style.borderLeftColor = cell.primaryColour;
                elements[i].style.borderBottomColor = cell.primaryColour;
                selectedCustomisations[2] = cell.customisationId;
            }
            break;
    }
    //saves updated customisation
    ajaxCallSaveCustomisations(selectedCustomisations[0] + "," + selectedCustomisations[1] + "," + selectedCustomisations[2]);
}


function addPlant() {
    let plantButton = document.getElementById("plant-selected-button");
    let emptyPopup = document.getElementById("empty-popup");
    let selectedForestCell = emptyPopup.selectedCell;
    let selectedPlantId = plantButton.selectedPlantId;

    //changes to the grid
    selectedForestCell.plantId = plantButton.selectedPlantId;
    selectedForestCell.plantGrowthStage = 0; //0, 1, or 2
    selectedForestCell.plantRequirement = 1; //0 if no requirement, 1 for fertiliser, etc
    selectedForestCell.plantImagePath = media_url + "forest_assets/id0.png";
    document.getElementById("forest-image-" + selectedForestCell.gridNumber).src = selectedForestCell.plantImagePath;   //sets image to seedling


    closePopup(emptyPopup);

    //changes to the database
    //updating inventory
    ajaxCallUpdateInv(selectedPlantId);
    ajaxCallUpdateInvOnPage();
    //update the plant selection grid in the popup
    let plantCount = document.getElementById("plant-count-" + selectedPlantId);
    const userInv = document.getElementById("retrieved-inventory-content").innerHTML.split(",");
    plantCount.innerHTML = "x" + userInv[8 + Number(selectedPlantId)];

    //updating forest
    makeForestChange(selectedForestCell.gridNumber, [selectedPlantId, selectedForestCell.plantGrowthStage, selectedForestCell.plantRequirement])
}

function giveResource() {
    const currentCell = document.getElementById("empty-popup").selectedCell;
    const resourceType = plantArray[currentCell.plantId][1];
    ajaxCallUpdateInvOnPage();
    const userInv = document.getElementById("retrieved-inventory-content").innerHTML.split(",");
    let userResources = [userInv[7], userInv[6], userInv[8]];   //water, treeguard, fertilizer

    if (currentCell.plantRequirement == 1 && userResources[resourceType] > 0) {    //if plant needs resource
        //marks plant as given resource
        currentCell.plantRequirement = 0;

        ajaxCallUseConsumeable(resourceType);
        ajaxCallUpdateInvOnPage();

        makeForestChange(currentCell.gridNumber, [currentCell.plantId, currentCell.plantGrowthStage, currentCell.plantRequirement])

        //update on page
        const resourceButton = document.getElementById("selected-plant-requirement-button");
        resourceButton.innerHTML = "Plant seems happy!";
        resourceButton.disabled = true;

    }
}

function openPopup(popup) {
    //check if recycling popup is open
    let recyclingPopup = document.getElementById("recycling-popup");
    if (recyclingPopup.style.display == "block") {
        recyclingPopup.style.animation = "recycling-exit 0.5s";
        setTimeout(function () { recyclingPopup.style.display = "none"; }, 480);
    }
    //open popup
    popup.style.display = "block";
    popup.style.animation = "popup-enter 0.5s";
}

function closePopup(popup) {
    popup.style.animation = "popup-exit 0.5s";
    setTimeout(function () { popup.style.display = "none"; }, 480);
}


//drag and drop handlers ---------------------------------------------------------------------------------
function litterDragStart(event) {
    event.dataTransfer.clearData();
    event.dataTransfer.setData('text/plain', event.target.id);
    let litter = event.currentTarget;
    event.currentTarget.style.border = "#1da124";
    //highlighting correct bin
    switch (litter.litterType) {
        case 0:
            document.getElementById("plastic-recycling").style.height = "100%";
            document.getElementById("paper-recycling").style.opacity = "0.4";
            document.getElementById("compost-recycling").style.opacity = "0.4";
            break;
        case 1:
            document.getElementById("plastic-recycling").style.opacity = "0.4";
            document.getElementById("paper-recycling").style.height = "100%";
            document.getElementById("compost-recycling").style.opacity = "0.4";
            break;
        case 2:
            document.getElementById("paper-recycling").style.opacity = "0.4";
            document.getElementById("plastic-recycling").style.opacity = "0.4";
            document.getElementById("compost-recycling").style.height = "100%";
            break;
    }
}

function litterDragEnd(event) {
    let litter = event.currentTarget;
    litter.style.border = "none";

    //resetting bin styles
    document.getElementById("plastic-recycling").style.opacity = "1";
    document.getElementById("paper-recycling").style.opacity = "1";
    document.getElementById("compost-recycling").style.opacity = "1";

    document.getElementById("plastic-recycling").style.height = "90%";
    document.getElementById("paper-recycling").style.height = "90%";
    document.getElementById("compost-recycling").style.height = "90%";
}

//functions for generating items & grids -------------------------------------------------------------

function generateRecycling() {
    const litterContainer = document.getElementById("litter-container");
    const user_inv = document.getElementById("retrieved-inventory-content").innerHTML.split(',');
    // populates the container with unrecycled paper
    for (let i = 0; i < user_inv[0]; i++) {
        addRecycleable(i, 0);
    }
    // populates the container with unrecycled plastic
    for (let i = 0; i < user_inv[1]; i++) {
        addRecycleable(i, 1);
    }
    //populates the container with unrecycled compost
    for (let i = 0; i < user_inv[2]; i++) {
        addRecycleable(i, 2);
    }

    function addRecycleable(num, type) {
        let litterImg = document.createElement("img");
        const addedLitter = litterContainer.appendChild(litterImg);
        addedLitter.id = "added-litter-" + type + "-" + num;
        addedLitter.litterType = type
        addedLitter.draggable = "true";
        addedLitter.classList.add("litter");
        // places litter at a random point in the container
        addedLitter.style = "top: " + Math.random() * 60 + "%; left: " + + Math.random() * 90 + "%;";
        switch (addedLitter.litterType) {
            case 0:
                addedLitter.style.backgroundColor = "red";
                break;
            case 1:
                addedLitter.style.backgroundColor = "blue";
                break;
            case 2:
                addedLitter.style.backgroundColor = "green";
                break;
        }
        addedLitter.ondragstart = function () { litterDragStart(event) };
        addedLitter.ondragend = function () { litterDragEnd(event) };
    }
}

function generatePlantSelectionGrid(cols) {
    const userInv = document.getElementById("retrieved-inventory-content").innerHTML.split(",");
    const gridContainer = document.getElementById("plant-selection-grid");

    let userSeedInv = new Array();

    //skips the first empty array slot
    for (let i = 1; i < (plantArray.length - 1); i++) {  //cut out first empty item
        //creating seed inventory
        userSeedInv[i] = userInv[i + 8];      //skips the items that arent seeds

        //creating selection cells
        let gridCell = document.createElement("div");
        const addedCell = gridContainer.appendChild(gridCell);
        addedCell.className = "card col-lg-3 m-1 bg-light";

        addedCell.id = "plant-selection-cell-" + i;
        addedCell.selectedPlantId = plantArray[i][0];
        addedCell.selectedPlantResource = plantArray[i][1];
        addedCell.selectedPlantRarity = plantArray[i][2];
        addedCell.selectedPlantName = plantArray[i][3];
        addedCell.selectedPlantCount = userSeedInv[i];
        addedCell.addEventListener("click", function () { onPlantCellClick(addedCell); });

        //getting images of plants
        const cellImage = addedCell.appendChild(document.createElement("img"));
        cellImage.className = "object-fit-cover";
        cellImage.src = media_url + "forest_assets/id" + addedCell.selectedPlantId + "_2.png";
        if (userSeedInv[i] == 0) {
            addedCell.style.border = "2px dashed rgba(109, 109, 109, 0.34)";
        }

        let plantCount = addedCell.appendChild(document.createElement("div"));
        plantCount.className = "position-absolute translate-middle badge rounded-pill bg-primary";
        plantCount.style = "top: 16px; left: 24px;";
        plantCount.id = "plant-count-" + i;
        plantCount.innerHTML = "x" + userSeedInv[i];

        let plantButton = document.getElementById("plant-selected-button");
        plantButton.selectedPlantId = addedCell.selectedPlantId;
    }
}

function generateCustomisationGrid() {
    const customisationList = document.getElementById("retrieved-customisation-content").innerHTML;
    const skyContainer = document.getElementById("customise-grid-sky");
    const landContainer = document.getElementById("customise-grid-land");
    const gridContainer = document.getElementById("customise-grid-grid");
    let i = 0;
    //every customisation in the database
    for (const item of customisationList.split(";")) {
        let currentCustomisation = item.split(",");
        let currentCell = document.createElement("div");
        //decide whether it is a sky, land or grid customisation
        switch (currentCustomisation[1]) {
            case "0":   //sky
                let skyCell = skyContainer.appendChild(currentCell);
                createCustomCell(skyCell, "sky");
                break;
            case "1":   //ground
                let landCell = landContainer.appendChild(currentCell);
                createCustomCell(landCell, "land");
                break;
            case "2":   //grid
                let gridCell = gridContainer.appendChild(currentCell);
                createCustomCell(gridCell, "grid");
                break;
        }

        function createCustomCell(cell, cellType) {
            cell.className = "btn";
            cell.id = "custom-" + cellType + "-cell-" + i++;
            cell.customisationId = currentCustomisation[0];
            cell.customisationType = currentCustomisation[1];
            cell.primaryColour = currentCustomisation[2];
            cell.secondaryColour = currentCustomisation[3];
            cell.style.backgroundImage = "linear-gradient(" + cell.primaryColour + ", " + cell.secondaryColour + ")";
            cell.addEventListener("click", function () { onCustomiseCellClick(cell); });
        }

    }
}

// generate user's forest grid 
function generateForestGrid(rows, cols) {
    const gridContainer = document.getElementById("forest-grid");
    //splits data into arrays for each plant
    const userForest = document.getElementById("retrieved-forest-content").innerHTML.split(";");
    gridContainer.style.setProperty('--forest-rows', rows);
    gridContainer.style.setProperty('--forest-cols', cols);
    let forestContainer = document.getElementById("forest-images");
    // iterates for each cell that will be in the grid
    for (let i = 0; i < (rows * cols); i++) {
        let gridCell = document.createElement("div");
        const addedCell = gridContainer.appendChild(gridCell);
        addedCell.className = "grid-item";
        addedCell.id = "forest-cell-" + i;  //unique cell id
        addedCell.gridNumber = i;           //used to refer to children
        addedCell.addEventListener("click", function () { onForestCellClick(addedCell); })

        let currentPlant = userForest[i].split(",");

        //creating each image
        const plantImage = document.createElement("img");
        let addedPlantImage = forestContainer.appendChild(plantImage);

        addedCell.plantId = currentPlant[0]; // id of plant in cell, 0 if none
        addedCell.plantGrowthStage = currentPlant[1]; //0, 1, or 2
        addedCell.plantRequirement = currentPlant[2]; //0 if plant is fed, 1 if needs resource
        //getting plant details from the plant table
        //if cell contains plant
        if (currentPlant[0] != 0) {
            //check if plant is first stage and assign appropriate image
            if (addedCell.plantGrowthStage == 0) {
                addedCell.plantImagePath = media_url + "forest_assets/id0.png";
            }
            else {
                addedCell.plantImagePath = media_url + "forest_assets/id" + addedCell.plantId + "_" + addedCell.plantGrowthStage + ".png";
            }
        }
        else {
            addedCell.plantImagePath = media_url + "forest_assets/empty.png";
        }

        //placing images in correct place
        addedPlantImage.id = "forest-image-" + i;
        addedPlantImage.classList.add("plant-image");
        addedPlantImage.src = addedCell.plantImagePath;
        let cellRect = addedCell.getBoundingClientRect();
        let forestRect = forestContainer.getBoundingClientRect();
        addedPlantImage.style = "top: " + ((100 * ((cellRect.top - forestRect.top) / forestRect.height)) - 37) + "%; left: " + ((100 * ((cellRect.left - forestRect.left) / forestRect.width))) + "%;";

    }
}

//reload and save to databases ------------------------------------------------------------------------

//plantLocation - cell 0-15, plantDetails - [plantId, growthStage (0,1,2), requirement(0,1)]
function makeForestChange(plantLocation, plantDetails) {
    ajaxCallUpdateForestData();

    //reading database entry
    const userForest = document.getElementById("retrieved-forest-content").innerHTML.split(";");

    //applying changes
    userForest[plantLocation] = plantDetails[0] + "," + plantDetails[1] + "," + plantDetails[2]

    //rebuilding database entry
    let forestString = "";
    for (let i = 0; i < userForest.length; i++) {
        forestString += userForest[i] + ";";
    }
    forestString = forestString.substring(0, forestString.length - 1);  //remove last ;
    //save foreststring
    ajaxCallSaveForest(forestString);
    ajaxCallUpdateForestData();
}

function sellForest() {
    // adds the value of the forest to the user's token balance, and resets the grid on the page and database
    // adding the value will be done in django, as will resetting the user's forest in the database
    // then the grid's contents should update to reflect the changes
    const value = document.getElementById("retrieved-value").innerHTML;
    ajaxCallAddTokens(value);
    ajaxCallSaveForest("0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0");
    ajaxCallUpdateForestData();

    //resetting the visuals
    for (let i = 0; i < 16; i++) {
        console.log("forest cell clear" + i)
        let currentCell = document.getElementById("forest-cell-" + i)
        currentCell.plantId = 0; // id of plant in cell, 0 if none
        currentCell.plantGrowthStage = 0; //0, 1, or 2
        currentCell.plantRequirement = 0; //0 if no requirement, 1 for fertiliser, etc
        currentCell.plantImagePath = media_url + "forest_assets/empty.png";

        let currentPlantImage = document.getElementById("forest-image-" + i);
        currentPlantImage.src = currentCell.plantImagePath;
    }
}

function ajaxCallSaveCustomisations(customiseString) {
    $.ajax({
        url: "save_customisations",
        type: 'POST',
        cache: false,
        async: false,
        data: { 'selected_customisations': customiseString },
        success: function (response) {
            console.log("Response: ", response);
        },
        error: function (error) {
            console.log("encountered error when sending customisation data: ", error);
        }
    })
        .done(response => { console.log("saved this: " + customiseString) }); // we don't need to do anything with the response
}

function ajaxCallSaveForest(forestString) {
    $.ajax({
        url: "save",
        type: 'POST',
        cache: false,
        async: false,
        data: { 'user_forest_cells': forestString },
        success: function (response) {
            console.log("Response: ", response);
        },
        error: function (error) {
            console.log("encountered error when sending forest data: ", error);
        }
    })
        .done(response => { console.log("saved this: " + forestString) }); // we don't need to do anything with the response
}

function ajaxCallUpdateForestData() {
    $.ajax({
        url: "update_forest_on_page",
        type: 'GET',
        cache: false,
        async: false,
    })
        .done(response => {
            document.getElementById("retrieved-forest-content").innerHTML = response.user_forest;
            document.getElementById("sell-value").innerHTML = "Current value of your forest: " + response.forest_value + " tokens."
            console.log("loaded this: " + response.user_forest);
        });
}

function ajaxCallAddTokens(tokens) {
    $.ajax({
        url: "add_tokens",
        type: 'POST',
        data: { 'number_of_tokens': tokens },
        success: function (response) {
            console.log("Response: ", response);
        },
        error: function (error) {
            console.log("encountered error when sending the number of tokens to add to the user's balance: ", error);
        }
    })
        .done(response => { console.log(response) })
}

function ajaxCallUpdateInv(plantId) {
    $.ajax({
        url: "remove_from_inv",
        type: 'POST',
        cache: false,
        async: false,
        data: { 'plant_id': plantId },
        success: function (response) {
            console.log("Response: ", response);
        },
        error: function (error) {
            console.log("encountered error when updating inventory after planting seedling: ", error);
        }
    })
        .done(response => { console.log(response) })
}

function ajaxCallUpdateInvOnPage() {
    $.ajax({
        url: "update_inventory_on_forest",
        type: 'GET',
        cache: false,
        async: false,
    })
        .done(response => {
            document.getElementById("retrieved-inventory-content").innerHTML = response.user_inventory;
            console.log("loaded this: " + response.user_inventory);
        });
}

function ajaxCallUseConsumeable(consumeable_id) {
    $.ajax({
        url: "use_consumeable",
        type: 'POST',
        cache: false,
        async: false,
        data: { 'consumeable_id': consumeable_id },
        success: function (response) {
            console.log("Response: ", response);
        },
        error: function (error) {
            console.log("encountered error when updating inventory after using consumeable: ", error);
        }
    })
        .done(response => { console.log(response) })
}

// initalisation -----------------------------------------------------------------------------------------------------------------

function getPlants() {
    let plantList = document.getElementById("retrieved-plant-content").innerHTML.split(";");
    var plantArray = new Array(plantList.length);
    for (let i = 0; i < plantList.length; i++) {    //ignore first item, no plant has id=0
        plantArray[i + 1] = plantList[i].split(",");  //creates list where id corresponds to index, [[id, requirement_type, rarity, plant_name]]
    }
    return plantArray;
}

function loadCustomisations() {
    //load all customisations to get the correct id
    const customisationList = document.getElementById("retrieved-customisation-content").innerHTML;
    let selectedCustomisations = document.getElementById("retrieved-selected-customisation-content").innerHTML.split(",");
    let i = 0;
    //for every customisation in the database
    for (const item of customisationList.split(";")) {
        let currentCustomisation = item.split(",");

        if (currentCustomisation[0] == selectedCustomisations[0]) {             //if currentCustomisation is selected sky customisation
            document.getElementById("forest-view").style.backgroundImage = "linear-gradient(" + currentCustomisation[2] + ", " + currentCustomisation[3] + ")";
        }
        else if (currentCustomisation[0] == selectedCustomisations[1]) {        //if currentCustomisation is selected land customisation
            document.getElementById("forest-floor-texture").style.backgroundColor = currentCustomisation[2];
            document.getElementById("forest-background-left").style.backgroundColor = currentCustomisation[3];
            //brighten secondary colour for lighter side of column
            let colorValue = parseInt(currentCustomisation[3].slice(1), 16);                   //remove # from start
            let adjustment = 40;                                                                //increase brightness by 40%
            let tertColor = "#" + (((colorValue & 0x0000FF) + adjustment) |
                ((((colorValue >> 8) & 0x00FF) + adjustment) << 8) |
                (((colorValue >> 16) + adjustment) << 16)).toString(16);
            document.getElementById("forest-background-right").style.backgroundColor = tertColor;
        }
        else if (currentCustomisation[0] == selectedCustomisations[2]) {        //if currentCustomisation is selected grid customisation
            //apply colours to every grid item
            let elements = document.getElementsByClassName("grid-item");
            for (var j = 0; j < elements.length; j++) {
                //sets the "top" and "bottom" of rotated grid to each colour
                elements[j].style.borderTopColor = currentCustomisation[3];
                elements[j].style.borderRightColor = currentCustomisation[3];
                elements[j].style.borderLeftColor = currentCustomisation[2];
                elements[j].style.borderBottomColor = currentCustomisation[2];
            }
        }
    }
}



    let plantArray = getPlants(); //[[plantid, requirement_type, rarity, plant_name]]
    generateForestGrid(4, 4);
    generatePlantSelectionGrid(2);
    generateRecycling();
    generateCustomisationGrid()
    loadCustomisations();

    document.getElementById("empty-popup").selectedCell = null;
    document.getElementById("customise-button").addEventListener("click", onCustomiseClick);
    document.getElementById("sell-button").addEventListener("click", onSellClick);
    document.getElementById("recycling-button").addEventListener("click", onRecyclingClick);
    document.getElementById("plant-selected-button").addEventListener("click", addPlant);
    document.getElementById("selected-plant-requirement-button").addEventListener("click", giveResource);
    document.getElementById("close-recycling-popup").addEventListener("click", function () { closePopup(document.getElementById("recycling-popup")) });
    document.getElementById("close-occupied-popup").addEventListener("click", function () { closePopup(document.getElementById("occupied-popup")) });
    document.getElementById("close-empty-popup").addEventListener("click", function () { closePopup(document.getElementById("empty-popup")) });
    document.getElementById("close-customise-popup").addEventListener("click", function () { closePopup(document.getElementById("customise-popup")) });
    document.getElementById("close-sell-popup").addEventListener("click", function () { closePopup(document.getElementById("sell-popup")) });
    document.getElementById("sell-forest-button").addEventListener("click", sellForest);
