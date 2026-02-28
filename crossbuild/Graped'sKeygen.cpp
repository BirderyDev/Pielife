#include <Core/Core.h>
#include <plugin/sqlite3/Sqlite3.h>
#include <windows.h>
#include <wininet.h>

#pragma comment(lib, "wininet.lib")

using namespace Upp;

String GenerateTicketID() {
    const String characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    String ticketID;

    for (int i = 0; i < 5; ++i)
        ticketID += characters[Random(characters.GetCount())];
    ticketID += '-';
    for (int i = 0; i < 5; ++i)
        ticketID += characters[Random(characters.GetCount())];
    ticketID += '-';
    for (int i = 0; i < 5; ++i)
        ticketID += characters[Random(characters.GetCount())];
    ticketID += '-';
    for (int i = 0; i < 5; ++i)
        ticketID += characters[Random(characters.GetCount())];

    return ticketID;
}

bool CheckTicketValidity(const String& ticketID, String& email) {
    String url = "https://onehouronelife.com/ticketServer/server.php?action=show_downloads&ticket_id=" + ticketID;
    HINTERNET hInternet = NULL, hConnect = NULL;
    DWORD bytesRead = 0;
    char buffer[4096];

    hInternet = InternetOpenA("Ticket Checker", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (hInternet == NULL) {
        LOG("InternetOpen failed.");
        return false;
    }

    hConnect = InternetOpenUrlA(hInternet, url.ToStd().c_str(), NULL, 0, INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE, 0);
    if (hConnect == NULL) {
        LOG("InternetOpenUrl failed.");
        InternetCloseHandle(hInternet);
        return false;
    }

    String response;
    while (InternetReadFile(hConnect, buffer, sizeof(buffer) - 1, &bytesRead) && bytesRead > 0) {
        buffer[bytesRead] = '\0';
        response.Cat(buffer);
    }

    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInternet);

    int pos = response.Find("Your account email is:");
    if (pos >= 0) {
        int start = response.Find("<b>", pos);
        int end = response.Find("</b>", start);
        if (start >= 0 && end > start) {
            email = response.Mid(start + 3, end - (start + 3));
            return true;
        }
    }
    return false;
}

void LogValidTicket(const String& ticketID, const String& email) {
    FileAppend file;
    if (file.Open("valid_tickets.txt")) {
        file << "Ticket: " << ticketID << " Email: " << email << '\n';
        file.Close();
    } else {
        LOG("Failed to open valid_tickets.txt for writing.");
    }
}

CONSOLE_APP_MAIN
{
    StdLogSetup(LOG_COUT | LOG_FILE);

    Sqlite3Session db;
    if (!db.Open("tickets.db")) {
        LOG("Can't create or open database file");
        return;
    }
    SQL = db;

    SQL.Execute("CREATE TABLE IF NOT EXISTS checked_tickets (ticket TEXT PRIMARY KEY)");

    SqlId table_checked_tickets("checked_tickets");
    SqlId ticket_column("ticket");

    while (true) {
        String ticketID = GenerateTicketID();

        SqlBool where = ticket_column == ticketID;
        SQL * Select(SqlAll()).From(table_checked_tickets).Where(where);
        if (SQL.Fetch()) {
            continue;
        }

        SQL * Insert(table_checked_tickets)(ticket_column, ticketID);

        String email;
        bool isValid = CheckTicketValidity(ticketID, email);

        if (isValid) {
            LogValidTicket(ticketID, email);

            LOG("Valid Ticket: " << ticketID << " Email: " << email);
        }

        LOG("Checked Ticket: " << ticketID << " - " << (isValid ? "Valid" : "Invalid"));
    }
}