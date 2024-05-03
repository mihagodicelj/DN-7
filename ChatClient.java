import java.io.*;
import java.net.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

import org.json.*;

public class ChatClient extends Thread
{
	protected int serverPort = 1234;

	public static void main(String[] args) throws Exception {
		new ChatClient();
	}

	public ChatClient() throws Exception {
		Socket socket = null;
		DataInputStream in = null;
		DataOutputStream out = null;

		BufferedReader std_in = new BufferedReader(new InputStreamReader(System.in));
		System.out.print("prosim, vpišite svoje uporabniško ime:");
		String ime = std_in.readLine();
		// connect to the chat server
		try {
			System.out.println("[system] connecting to chat server ...");
			socket = new Socket("localhost", serverPort); // create socket connection
			in = new DataInputStream(socket.getInputStream()); // create input stream for listening for incoming messages
			out = new DataOutputStream(socket.getOutputStream()); // create output stream for sending messages
			System.out.println("[system] connected");

			this.sendMessage("uporabnik " + ime + " se je povezal", out); // send the message to the chat server


			ChatClientMessageReceiver message_receiver = new ChatClientMessageReceiver(in); // create a separate thread for listening to messages from the chat server
			message_receiver.start(); // run the new thread
		} catch (Exception e) {
			e.printStackTrace(System.err);
			System.exit(1);
		}

		// read from STDIN and send messages to the chat server
		String userInput;
		while ((userInput = std_in.readLine()) != null) { // read a line from the console
			this.sendMessage(userInput, out); // send the message to the chat server
		}

		// cleanup
		out.close();
		in.close();
		std_in.close();
		socket.close();
	}

	private void sendMessage(String sender, String type, String content, DataOutputStream out) {
    try {
        JSONObject messageJson = new JSONObject();
        messageJson.put("sender", sender);
        messageJson.put("time", getCurrentTime());
        messageJson.put("type", type);
        messageJson.put("content", content);
        
        out.writeUTF(messageJson.toString()); // Send the JSON message as a string
        out.flush(); // Ensure the message has been sent
    } catch (IOException | JSONException e) {
        System.err.println("[system] could not send message");
        e.printStackTrace(System.err);
    }
}

// Helper method to get current time in a formatted string
private String getCurrentTime() {
    DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    Date date = new Date();
    return dateFormat.format(date);
}

}

// wait for messages from the chat server and print the out
class ChatClientMessageReceiver extends Thread {
    private DataInputStream in;

    public ChatClientMessageReceiver(DataInputStream in) {
        this.in = in;
    }

    public void run() {
        try {
            String message;
            while ((message = this.in.readUTF()) != null) { // Read new message
                JSONObject messageJson = new JSONObject(message); // Parse JSON message
                String sender = messageJson.getString("sender");
                String time = messageJson.getString("time");
                String type = messageJson.getString("type");
                String content = messageJson.getString("content");
                
                // Print the parsed message to the console
                System.out.println("[" + time + "] " + sender + ": " + content);
            }
        } catch (IOException | JSONException e) {
            System.err.println("[system] could not read message");
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }
}
