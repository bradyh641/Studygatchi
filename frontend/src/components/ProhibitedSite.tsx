import { useEffect, useState } from "react";

const STORAGE_KEY = "prohibitedSites";

const normalizeHostname = (value: string): string => {
  const input = value.trim();
  if (!input) {
    throw new Error("Enter a website URL.");
  }

  const parsed = new URL(input.includes("://") ? input : `https://${input}`);
  if (!["http:", "https:"].includes(parsed.protocol) || !parsed.hostname) {
    throw new Error("Enter a valid website URL.");
  }

  return parsed.hostname.replace(/\.$/, "").toLowerCase();
};

const getStoredSites = async (): Promise<string[]> => {
  if (typeof chrome === "undefined" || !chrome.storage?.local) {
    throw new Error("Chrome storage is unavailable. Load the app as an extension.");
  }

  const result = await chrome.storage.local.get(STORAGE_KEY);
  const sites = result[STORAGE_KEY];
  return Array.isArray(sites) ? sites.filter((site): site is string => typeof site === "string") : [];
};

const saveStoredSites = async (sites: string[]): Promise<void> => {
  await chrome.storage.local.set({ [STORAGE_KEY]: sites });
};

export default function ProhibitedSite() {
  const [sites, setSites] = useState<string[]>([]);
  const [hostname, setHostname] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSites = async () => {
      try {
        setSites((await getStoredSites()).sort());
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load prohibited sites.");
      } finally {
        setLoading(false);
      }
    };

    void loadSites();
  }, []);

  const addSite = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage("");

    try {
      const normalizedHostname = normalizeHostname(hostname);
      const currentSites = await getStoredSites();
      if (currentSites.includes(normalizedHostname)) {
        setMessage("That site is already prohibited.");
        return;
      }

      const updatedSites = [...currentSites, normalizedHostname].sort();
      await saveStoredSites(updatedSites);
      setSites(updatedSites);
      setHostname("");
      setMessage("Site added.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to add prohibited site.");
    }
  };

  const removeSite = async (site: string) => {
    setMessage("");

    try {
      const updatedSites = (await getStoredSites()).filter((currentSite) => currentSite !== site);
      await saveStoredSites(updatedSites);
      setSites(updatedSites);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to remove prohibited site.");
    }
  };

  return (
    <section aria-labelledby="prohibited-sites-title">
      <h5 id="prohibited-sites-title">Prohibited Sites</h5>
      <form onSubmit={addSite} style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={hostname}
          onChange={(event) => setHostname(event.target.value)}
          placeholder="example.com"
          aria-label="Website URL"
        />
        <button type="submit">Add</button>
      </form>

      {message && <p role="status">{message}</p>}
      {loading ? (
        <p>Loading prohibited sites...</p>
      ) : (
        <ul>
          {sites.map((site) => (
            <li key={site}>
              <span>{site}</span>{" "}
              <button
                type="button"
                onClick={() => void removeSite(site)}
                aria-label={`Remove ${site}`}
              >
                -
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
