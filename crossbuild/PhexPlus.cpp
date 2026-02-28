// YummyLife: New PhexPlus (version 8) commands
    serverCommands["LIFE_PROFILE"].func = serverCmdLIFE_PROFILE;
    serverCommands["LIFE_PROFILE"].minWords = 4;
void Phex::serverCmdLIFE_PROFILE(std::vector<std::string> input) {
    printf("Packet: %s\n", joinStr(input).c_str());
    int life_id = stoi(input[1]);
    int deleteProfile = stoi(input[2]);
    std::string channel = input[3];
    createLifeProfile(life_id, channel);

    // Delete the profile if requested
    if (deleteProfile) {
        lifeIdToProfiles.erase(life_id);
        return;
    }

    LifeProfile &profile = lifeIdToProfiles[life_id];

    // Go over the rest of the parameters and set the profile fields
    for (size_t i = 4; i < input.size(); ++i) {
        std::string param = input[i];

        // Make sure the parameter is in the form "key=value"
        size_t pos = param.find('=');
        if (pos == std::string::npos) {
            continue; // Invalid parameter format
        }

        std::string key = param.substr(0, pos);
        std::string value = param.substr(pos + 1);

        if (key == "ti") profile.title = value;
        else if (key == "op") profile.opinion = std::stoi(value);
        else if (key == "tc")
            sscanf(value.c_str(), "%f,%f,%f,%f", &profile.tagColor[0], &profile.tagColor[1], &profile.tagColor[2], &profile.tagColor[3]);
        else if (key == "si") profile.specialID = std::stoi(value);
        else if (key == "cn") profile.cursename = value;
        else if (key == "ln") profile.leaderboardname = value;
        else if (key == "li") profile.leaderboardID = value;
    }
}
void Phex::joinChannel(std::string inChannelName) {
    if (channelName.length() > 0) tcp.send("LEAVE "+channelName);
    channelName = inChannelName;
    tcp.send("JOIN "+channelName);
    mainChatWindow.clear();
    tcp.send("GETLAST "+channelName+" 30");
    sendServerLife(bSendFakeLife ? 1 : HetuwMod::ourLiveObject->id);
    if (!HetuwMod::phexSkipTOS) {
        tcp.send("USER_CMD tos");
    }
    lifeIdToProfiles.clear(); // Sendinf GET_LIFE_PROFILES will get us all of them again
    // First Phex protocol that supports life profiles is 8; PhexPlus
    if(HetuwMod::bRequestLifeProfiles){
        tcp.send("GET_LIFE_PROFILES "+channelName+" 1");
    }
    if(HetuwMod::bIdentifyMyself){
        tcp.send("USER_CMD identify");
    }
}