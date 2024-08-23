import streamlit as st
import base64
import hashlib
from PIL import Image
from io import BytesIO
from datetime import datetime as dt  # Import the datetime class
import time

# Define your Block and Blockchain classes here
class Block:
    def __init__(self, data, previous_hash):
        self.timestamp = dt.now()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self._hash_block()

    def _hash_block(self):
        # Create a hash of the block contents
        sha = hashlib.sha256()
        hash_string = str(self.timestamp) + str(self.data) + str(self.previous_hash)
        sha.update(hash_string.encode('utf-8'))
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self._create_genesis_block()]

    def _create_genesis_block(self):
        return Block("Genesis Block", None)

    def add_block(self, data):
        previous_hash = self.chain[-1].hash
        self.chain.append(Block(data, previous_hash))

    def get_blocks(self):
        return [
            (block.data, block.timestamp, block.hash, block.previous_hash) 
            for block in self.chain
        ]
    
    def tamper_block(self, block_index, new_data):
        if 0 < block_index < len(self.chain):
            self.chain[block_index].data = new_data
            self.chain[block_index].hash = self.chain[block_index]._hash_block()

    def verify_integrity(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

# Initialize blockchain in session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

# Blockchain Management Functions
def blockchain_page():
    st.title("Blockchain Voting Management")

    # Initialize variables
    data = None

    # Step 3: Add Data to Blockchain
    if data and st.button("Vote Candidate"):
        combined_data = f"{data}"
        st.session_state.blockchain.add_block(combined_data)
        st.success("Data added to the blockchain")

# Function to test data integrity
def test_data_integrity():
    st.title("Test Data Integrity")

    if len(st.session_state.blockchain.chain) > 1:
        # Tamper with the blockchain data
        tamper_index = st.number_input("Enter the index of the block to tamper with", min_value=1, max_value=len(st.session_state.blockchain.chain)-1, value=1)
        tampered_data = st.text_input("Enter new data for the tampered block")

        if st.button("Tamper with Block"):
            st.session_state.blockchain.tamper_block(tamper_index, tampered_data)
            st.write(f"Block at index {tamper_index} has been tampered with.")

        if st.button("Verify Blockchain Integrity"):
            start_time = time.perf_counter()
            integrity_status = st.session_state.blockchain.verify_integrity()
            
            if integrity_status:
                st.success("Blockchain integrity is intact.")
            else:
                st.error("Blockchain integrity has been compromised.")
            
            end_time = time.perf_counter()
            verification_time = end_time - start_time
            
            st.write(f"Time taken to verify blockchain integrity: {verification_time:.4f} seconds")
    else:
        st.write("Not enough blocks to tamper with. Please add more blocks to the blockchain.")

# Function to register a candidate
def registerCandidate(candidate_data, candidateName, candidateID, candidateGPA, candidatePhoto, candidateVision, candidateMission):
    current_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp

    # Check if any mandatory field is empty
    if not (candidateName and candidateID and candidateGPA and candidatePhoto and candidateVision and candidateMission):
        st.error("Please fill out all fields in the form!")
        return

    # Check if the candidateID already exists
    if candidateID in candidate_data:
        st.error("Candidate with the same ID already exists. Please choose a different ID.")
        return

    # Check if the candidateName already exists
    if any(candidateName.lower() == data['candidateName'].lower() for data in candidate_data.values()):
        st.error("Candidate with the same name already exists. Please choose a different name.")
        return

    # Check if candidateID length is 10
    if len(candidateID) != 10:
        st.error("Candidate ID must be 10 characters long.")
        return

    # Check if candidateGPA is within the valid range
    if not (0.0 <= candidateGPA <= 4.0):
        st.error("Candidate GPA must be between 0.0 and 4.0.")
        return

    # Check if candidateGPA meets the minimum requirement
    if candidateGPA < 3.5:
        st.error("Candidate GPA must be at least 3.5.")
        return

    # Add the candidate to the data with the timestamp
    candidate_data[candidateID] = {
        'candidateName': candidateName,
        'candidateGPA': candidateGPA,
        'candidatePhoto': candidatePhoto,  # Save the base64-encoded photo
        'candidateVision': candidateVision,  # Save candidate vision
        'candidateMission': candidateMission,  # Save candidate mission
        'timestamp': current_time  # Save the registration timestamp
    }
    st.success(f"Candidate {candidateName} with ID {candidateID} registered successfully at {current_time}.")

# Function to vote for a candidate
def voteCandidate(voter_data, candidate_data, blockchain, voterName, voterID, voterClass, voterContact, selected_candidate):
    current_time = dt.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp

    # Check if the selected candidate is valid
    if selected_candidate not in candidate_data:
        st.error("Invalid candidate selected. Please choose a candidate from the registered candidates.")
        return

    # Check if the voterName already exists
    if any(voterName.lower() == voter_data[voterID]['voterName'].lower() for voterID in voter_data):
        st.error("Your name already registered. You can only vote once.")
        return

    # Check if the voterID already exists
    if voterID in voter_data:
        st.error("Your ID already registered. You can only vote once.")
        return
    
    # Check if candidateID length is 10
    if len(voterID) != 10:
        st.error("Voter ID must be 10 characters long.")
        return

    # Check if the voterContact already exists
    if any(voterContact.lower() == voter_data[voterID]['voterContact'].lower() for voterID in voter_data):
        st.error("Your phone number already registered. You can only vote once.")
        return

    # Add the vote to the data with the timestamp
    voter_data[voterID] = {
        'voterName': voterName,
        'voterClass': voterClass,
        'voterContact': voterContact,
        'selectedCandidate': selected_candidate,
        'timestamp': current_time  # Save the vote timestamp
    }

    # Create a string representation of the vote data
    vote_data_str = f"Vote : {voterName} ({voterID}) voted for {candidate_data[selected_candidate]['candidateName']} at {current_time}"

    # Add the vote data to the blockchain
    blockchain.add_block(vote_data_str)

    st.success(f"Vote cast successfully")

# Function to show all registered candidates
def showRegisteredCandidates(candidate_data):
    st.header("Registered Candidates")

    if not candidate_data:
        st.info("No candidates registered yet.")
    else:
        num_columns = len(candidate_data)
        columns = st.columns(num_columns)

        for i, (candidateID, data) in enumerate(candidate_data.items()):
            with columns[i % num_columns]:
                st.write(f"**ID :** {candidateID}")
                st.write(f"**Name :** {data['candidateName']}")
                st.write(f"**GPA :** {data['candidateGPA']}")
                if 'candidatePhoto' in data:
                    # Decode the base64-encoded photo
                    decoded_photo = base64.b64decode(data['candidatePhoto'])
                    # Display the photo using PIL Image
                    image = Image.open(BytesIO(decoded_photo))
                    st.image(image, caption=f"Photo of {data['candidateName']}", use_column_width=True)
                if 'candidateVision' in data:
                    st.write(f"**Vision :**\n\n {data['candidateVision']}")
                if 'candidateMission' in data:
                    st.write(f"**Mission :**\n\n {data['candidateMission']}")
                st.write(f"**Timestamp :** {data.get('timestamp', 'N/A')}")
                st.write("------")

# Function to determine and display the winner and other candidates
def showResults(candidate_data, voter_data):
    st.header("Election Results")

    if not voter_data:
        st.info("No votes cast yet. Cannot determine the winner.")
    else:
        # Count votes for each candidate
        candidate_votes = {candidateID: 0 for candidateID in candidate_data.keys()}
        
        for voterID, data in voter_data.items():
            selected_candidate = data['selectedCandidate']
            candidate_votes[selected_candidate] += 1

        # Find the candidate with the maximum votes (the winner)
        winner_candidate_id = max(candidate_votes, key=candidate_votes.get)
        winner_candidate_name = candidate_data[winner_candidate_id]['candidateName']
        winner_vote_count = candidate_votes[winner_candidate_id]

        st.success(f"The winner is {winner_candidate_name} with {winner_vote_count} votes.")

        # Display vote counts for all candidates
        st.subheader("Vote Counts for All Candidates")
        for candidateID, data in candidate_data.items():
            candidate_name = data['candidateName']
            vote_count = candidate_votes[candidateID]
            st.write(f"{candidate_name} : {vote_count} votes")

# Function to show data that added to Blockchain
def view_blockchain_page():
    st.header("View Blockchain Data")

    # Add authentication inputs
    username = st.text_input("Enter Username:", type="password")
    password = st.text_input("Enter Password:", type="password")

    # Hardcoded example username and password (replace with your authentication logic)
    valid_username = "admin"
    valid_password = "admin"

    if st.button("Authenticate"):
        if username == valid_username and password == valid_password:
            # Display blockchain data only if authentication is successful
            for blockchainData, timestamp, block_hash, prev_hash in st.session_state.blockchain.get_blocks():
                st.write(f"Blockchain data :\n\n {blockchainData}")
                st.write(f"Timestamp : {timestamp}")
                st.write(f"Hash : {block_hash}")
                st.write(f"Previous Hash : {prev_hash or 'None'}")
                st.write("-----")  # Separator for each block
        else:
            st.error("Authentication failed. Please check your username and password.")

# Streamlit UI
def main():
    st.title("E-Voting Management System")

    if 'candidate_data' not in st.session_state:
        st.session_state.candidate_data = {}

    if 'voter_data' not in st.session_state:
        st.session_state.voter_data = {}

    # Menu navigation
    menu_option = st.sidebar.selectbox("Select Function",
                                       ["Register Candidate", "Show Registered Candidates", "Vote Candidate", "View Blockchain", "Show Results", "Test Data Integrity"])

    if menu_option == "Register Candidate":
        st.header("Candidate Registration")
        candidateName = st.text_input("Enter Candidate Name:")
        candidateID = st.text_input("Enter Candidate ID:")
        candidateGPA = st.number_input("Enter Candidate GPA:", min_value=0.0, max_value=4.0, step=0.01)

        # Add text areas for vision and mission (set as required)
        candidateVision = st.text_area("Candidate Vision:", key="vision")
        candidateMission = st.text_area("Candidate Mission:", key="mission")

        candidatePhoto = st.file_uploader("Upload Candidate Photo", type=["jpg", "jpeg", "png"])

        if st.button("Register Candidate"):
            # Save the uploaded photo, vision, and mission
            photo_base64 = None
            vision_text = candidateVision.strip() if candidateVision else None
            mission_text = candidateMission.strip() if candidateMission else None

            if candidatePhoto is not None:
                photo_content = candidatePhoto.read()
                photo_base64 = base64.b64encode(photo_content).decode("utf-8")

            registerCandidate(st.session_state.candidate_data, candidateName, candidateID, candidateGPA, photo_base64, vision_text, mission_text)

    elif menu_option == "Show Registered Candidates":
        showRegisteredCandidates(st.session_state.candidate_data)

    # Vote Candidate Section
    elif menu_option == "Vote Candidate":
        st.header("Vote for a Candidate")
        voterName = st.text_input("Enter Your Name:")
        voterID = st.text_input("Enter Your ID:")
        voterClass = st.text_input("Enter Your Class:")
        voterContact = st.text_input("Enter Your Contact:")

        # Get the list of registered candidates with both ID and Name
        candidate_list = {candidateID: f"{data['candidateName']} ({candidateID})" for candidateID, data in st.session_state.candidate_data.items()}
        selected_candidate = st.selectbox("Select Candidate:", list(candidate_list.values()))

        # Extract the selected candidate ID
        matching_candidates = [k for k, v in candidate_list.items() if v == selected_candidate]

        if matching_candidates:
            selected_candidate_id = matching_candidates[0]
        else:
            st.error("Invalid candidate selected. Please choose a candidate from the registered candidates.")
            return

        # Display the selected candidate information and photo
        st.header("Selected Candidate Information")
        st.write(f"**ID :** {selected_candidate_id}")
        st.write(f"**Name :** {st.session_state.candidate_data[selected_candidate_id]['candidateName']}")
        st.write(f"**GPA :** {st.session_state.candidate_data[selected_candidate_id]['candidateGPA']}")
        if 'candidatePhoto' in st.session_state.candidate_data[selected_candidate_id]:
            # Decode and display the base64-encoded photo
            decoded_photo = base64.b64decode(st.session_state.candidate_data[selected_candidate_id]['candidatePhoto'])
            image = Image.open(BytesIO(decoded_photo))
            st.image(image, caption=f"Photo of {st.session_state.candidate_data[selected_candidate_id]['candidateName']}", use_column_width=True)
            st.write(f"**Vision :**\n\n {st.session_state.candidate_data[selected_candidate_id]['candidateVision']}")
            st.write(f"**Mission :**\n\n {st.session_state.candidate_data[selected_candidate_id]['candidateMission']}")
        st.write("------")

        if st.button("Vote"):
            voteCandidate(st.session_state.voter_data, st.session_state.candidate_data, st.session_state.blockchain, voterName, voterID, voterClass, voterContact, selected_candidate_id)
        
    # Show Winner from Voted Candidate
    elif menu_option == "Show Results":
        showResults(st.session_state.candidate_data, st.session_state.voter_data)

    # View Data that already added to Blockchain
    elif menu_option == "View Blockchain":
        view_blockchain_page()

    # Testing data integrity
    elif menu_option == "Test Data Integrity":
        test_data_integrity()

if __name__ == "__main__":
    main()