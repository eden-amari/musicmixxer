"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
	createPlaylist,
	deletePlaylist,
	exportPlaylist,
	fetchPlaylist,
	fetchPlaylists,
	fetchSpotifyPlaylistTracks,
	fetchSpotifyPlaylists,
	importFile,
	importSpotifyPlaylist,
	organizePlaylist,
	updatePlaylist,
} from "@/lib/api-client";
import { useAuth } from "@/components/providers/AuthProvider";
import {
	readPendingSpotifyToken,
	readSession,
	writePostSpotifyRedirect,
} from "@/lib/session-storage";
import type {
	OrganizedTrack,
	PlaylistDetail,
	PlaylistSummary,
	SpotifyPlaylist,
	SpotifyPlaylistTrack,
} from "@/lib/types";

type WorkspaceClientProps = {
	initialSection?: "dashboard" | "import" | "export";
};

export function WorkspaceClient({
	initialSection = "dashboard",
}: WorkspaceClientProps) {
	const { session } = useAuth();
	const spotifyToken = useMemo(() => {
		return (
			session?.spotifyToken ||
			readSession()?.spotifyToken ||
			readPendingSpotifyToken() ||
			""
		);
	}, [session?.spotifyToken]);
	const [playlists, setPlaylists] = useState<PlaylistSummary[]>([]);
	const [selectedId, setSelectedId] = useState<number | null>(null);
	const [selectedPlaylist, setSelectedPlaylist] = useState<PlaylistDetail | null>(null);
	const [organizedTracks, setOrganizedTracks] = useState<OrganizedTrack[]>([]);
	const [message, setMessage] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [busyAction, setBusyAction] = useState<string | null>(null);
	const [createForm, setCreateForm] = useState({ title: "", description: "" });
	const [editForm, setEditForm] = useState({ title: "", description: "" });
	const [organizeMode, setOrganizeMode] = useState("smart_mix");
	const [exportName, setExportName] = useState("");
	const [importSource, setImportSource] = useState<"spotify" | "csv" | "json">("spotify");
	const [importFormat, setImportFormat] = useState<"csv" | "json">("json");
	const [importText, setImportText] = useState("");
	const [useSpotifyEnrichmentForRawImport, setUseSpotifyEnrichmentForRawImport] = useState(false);
	const [importPlaylistMode, setImportPlaylistMode] = useState<"new" | "existing">("new");
	const [importTargetId, setImportTargetId] = useState<number | null>(null);
	const [importCreateForm, setImportCreateForm] = useState({ title: "", description: "" });
	const [spotifyPlaylists, setSpotifyPlaylists] = useState<SpotifyPlaylist[]>([]);
	const [spotifyPlaylistId, setSpotifyPlaylistId] = useState("");
	const [spotifyPlaylistTracks, setSpotifyPlaylistTracks] = useState<SpotifyPlaylistTrack[]>([]);
	const selectedSpotifyPlaylist =
		spotifyPlaylists.find((playlist) => playlist.id === spotifyPlaylistId) ?? null;
	const selectedSpotifyTrackCount =
		selectedSpotifyPlaylist && selectedSpotifyPlaylist.tracks_count > 0
			? selectedSpotifyPlaylist.tracks_count
			: spotifyPlaylistTracks.length;

	const formatImportMessage = useCallback(
		(
			sourceLabel: string,
			result: {
				total: number;
				success: number;
				duplicates: number;
				failed: number;
				queued_for_enrichment?: number;
			},
		) => {
			const parts = [
				`${sourceLabel} imported ${result.success} track${result.success === 1 ? "" : "s"}`,
				`${result.duplicates} duplicate${result.duplicates === 1 ? "" : "s"} skipped`,
			];

			if (result.failed > 0) {
				parts.push(`${result.failed} track${result.failed === 1 ? "" : "s"} failed`);
			}

			if (result.queued_for_enrichment) {
				parts.push(
					`${result.queued_for_enrichment} track${result.queued_for_enrichment === 1 ? "" : "s"} queued for Spotify enrichment`,
				);
			}

			parts.push(`${result.total} total checked`);

			return `${parts.join(", ")}.`;
		},
		[],
	);

	const loadSpotifyPlaylists = useCallback(async () => {
		const next = await fetchSpotifyPlaylists();
		setSpotifyPlaylists(next);
		if (!spotifyPlaylistId && next.length > 0) {
			setSpotifyPlaylistId(next[0].id);
		}
	}, [spotifyPlaylistId]);

	useEffect(() => {
		if (!spotifyToken) {
			setSpotifyPlaylists([]);
			setSpotifyPlaylistId("");
			setSpotifyPlaylistTracks([]);
		}
	}, [spotifyToken]);

	useEffect(() => {
		void refreshPlaylists();
	}, []);

	useEffect(() => {
		if (!selectedId && playlists.length > 0) {
			setSelectedId(playlists[0].id);
		}
	}, [playlists, selectedId]);

	useEffect(() => {
		if (!selectedPlaylist) {
			setEditForm({ title: "", description: "" });
			return;
		}

		setEditForm({
			title: selectedPlaylist.title,
			description: selectedPlaylist.description,
		});
	}, [selectedPlaylist]);

	useEffect(() => {
		if (
			initialSection === "import" &&
			importSource === "spotify" &&
			spotifyToken &&
			spotifyPlaylists.length === 0
		) {
			setBusyAction("spotify-list");
			setMessage(null);
			setError(null);
			void loadSpotifyPlaylists()
				.catch((nextError) => {
					setError(
						nextError instanceof Error
							? nextError.message
							: "Failed to load Spotify playlists.",
					);
				})
				.finally(() => setBusyAction(null));
		}
	}, [
		importSource,
		initialSection,
		loadSpotifyPlaylists,
		spotifyToken,
		spotifyPlaylists.length,
	]);

	useEffect(() => {
		if (
			initialSection !== "import" ||
			importSource !== "spotify" ||
			!spotifyToken
		) {
			return;
		}

		setMessage("Spotify connected. Loading your playlists...");
		setError(null);
		setBusyAction("spotify-list");

		void loadSpotifyPlaylists()
			.catch((nextError) => {
				setError(
					nextError instanceof Error
						? nextError.message
						: "Failed to load Spotify playlists.",
				);
			})
			.finally(() => setBusyAction(null));
	}, [importSource, initialSection, loadSpotifyPlaylists, spotifyToken]);

	useEffect(() => {
		if (
			initialSection === "import" &&
			importSource === "spotify" &&
			spotifyToken &&
			spotifyPlaylistId
		) {
			setBusyAction("spotify-tracks");
			setError(null);
			void fetchSpotifyPlaylistTracks(spotifyPlaylistId)
				.then((next) => setSpotifyPlaylistTracks(next))
				.catch((nextError) => {
					setError(
						nextError instanceof Error
							? nextError.message
							: "Failed to load Spotify playlist tracks.",
					);
				})
				.finally(() => setBusyAction(null));
		}
	}, [importSource, initialSection, spotifyPlaylistId, spotifyToken]);

	async function refreshPlaylists(preferredId?: number) {
		try {
			setError(null);
			const next = await fetchPlaylists();
			setPlaylists(next);
			if (preferredId) {
				setSelectedId(preferredId);
			}
		} catch (nextError) {
			setError(nextError instanceof Error ? nextError.message : "Failed to load playlists.");
		}
	}

	const loadPlaylist = useCallback(async (playlistId: number) => {
		try {
			setError(null);
			const detail = await fetchPlaylist(playlistId);
			setSelectedPlaylist(detail);
			setOrganizedTracks([]);
		} catch (nextError) {
			setError(nextError instanceof Error ? nextError.message : "Failed to load playlist.");
		}
	}, []);

	useEffect(() => {
		if (selectedId) {
			void loadPlaylist(selectedId);
		}
	}, [loadPlaylist, selectedId]);

	useEffect(() => {
		if (
			!selectedPlaylist ||
			selectedPlaylist.enrichment?.pending_tracks === undefined ||
			selectedPlaylist.enrichment.pending_tracks <= 0
		) {
			return;
		}

		const timeoutId = window.setTimeout(() => {
			void loadPlaylist(selectedPlaylist.id);
		}, 8000);

		return () => window.clearTimeout(timeoutId);
	}, [loadPlaylist, selectedPlaylist]);

	async function withBusy<T>(label: string, action: () => Promise<T>) {
		setBusyAction(label);
		setMessage(null);
		setError(null);
		try {
			return await action();
		} catch (nextError) {
			setError(nextError instanceof Error ? nextError.message : "Something went wrong.");
			return undefined;
		} finally {
			setBusyAction(null);
		}
	}

	async function ensureImportPlaylist() {
		if (importPlaylistMode === "existing") {
			if (!importTargetId) {
				throw new Error("Pick an existing playlist before importing.");
			}
			return importTargetId;
		}

		if (!importCreateForm.title.trim()) {
			throw new Error("Add a playlist title before importing raw data.");
		}

		const created = await createPlaylist({
			title: importCreateForm.title.trim(),
			description: importCreateForm.description.trim(),
		});
		setImportCreateForm({ title: "", description: "" });
		setImportPlaylistMode("existing");
		setImportTargetId(created.id);
		return created.id;
	}

	async function importRawText() {
		if (!importText.trim()) {
			throw new Error("Paste your raw playlist data before importing.");
		}

		if (useSpotifyEnrichmentForRawImport && !session?.spotifyToken) {
			throw new Error("Connect Spotify before using Spotify enrichment for CSV or JSON imports.");
		}

		const playlistId = await ensureImportPlaylist();
		const file = new File(
			[importText],
			`playlist-import.${importFormat === "json" ? "json" : "csv"}`,
			{
				type: importFormat === "json" ? "application/json" : "text/csv",
			},
		);
		const result = await importFile(importFormat, file, {
			playlistId,
			useSpotifyEnrichment: useSpotifyEnrichmentForRawImport,
		});
		setImportText("");
		await refreshPlaylists(result.playlist_id);
		setSelectedId(result.playlist_id);
		setMessage(formatImportMessage(importFormat.toUpperCase(), result));
	}

	async function importUploadedFile(file: File, kind: "csv" | "json") {
		if (useSpotifyEnrichmentForRawImport && !session?.spotifyToken) {
			throw new Error("Connect Spotify before using Spotify enrichment for CSV or JSON imports.");
		}

		const playlistId = await ensureImportPlaylist();
		const result = await importFile(kind, file, {
			playlistId,
			useSpotifyEnrichment: useSpotifyEnrichmentForRawImport,
		});
		await refreshPlaylists(result.playlist_id);
		setSelectedId(result.playlist_id);
		setMessage(formatImportMessage(kind.toUpperCase(), result));
	}

	async function handleSpotifyImport() {
		if (!spotifyPlaylistId) {
			throw new Error("Choose one of your Spotify playlists before importing.");
		}

		const result = await importSpotifyPlaylist(spotifyPlaylistId);
		await refreshPlaylists(result.playlist_id);
		setSelectedId(result.playlist_id);
		setMessage(formatImportMessage("Spotify playlist", result));
	}

	function connectSpotifyForImport() {
		writePostSpotifyRedirect("/organizePlaylist/import");
		window.location.assign("/api/backend/auth/spotify/login");
	}

	function connectSpotifyForExport() {
		writePostSpotifyRedirect("/organizePlaylist/export");
		window.location.assign("/api/backend/auth/spotify/login");
	}

	async function handlePlaylistUpdate() {
		if (!selectedPlaylist) {
			return;
		}

		const title = editForm.title.trim();
		if (!title) {
			throw new Error("Playlist title cannot be empty.");
		}

		await updatePlaylist(selectedPlaylist.id, {
			title,
			description: editForm.description.trim(),
		});
		await refreshPlaylists(selectedPlaylist.id);
		await loadPlaylist(selectedPlaylist.id);
		setMessage(`Updated playlist "${title}".`);
	}

	async function handlePlaylistDelete() {
		if (!selectedPlaylist) {
			return;
		}

		const playlistTitle = selectedPlaylist.title;
		await deletePlaylist(selectedPlaylist.id);
		const deletedId = selectedPlaylist.id;
		setSelectedPlaylist(null);
		setOrganizedTracks([]);
		const nextPlaylists = await fetchPlaylists();
		setPlaylists(nextPlaylists);
		const fallbackId =
			nextPlaylists.find((playlist) => playlist.id !== deletedId)?.id ?? null;
		setSelectedId(fallbackId);
		setMessage(`Deleted playlist "${playlistTitle}".`);
	}

	const currentTitle =
		initialSection === "dashboard"
			? "Your Library"
			: initialSection === "import"
				? "Import Raw Playlist Data"
				: "Export Playlist";

	return (
		<div className="page-shell2 flexColumnLeft workspace-shell">
			{/* <div className="workspace-status">
				{message ? <div className="notice success">{message}</div> : null}
				{error ? <div className="notice error">{error}</div> : null}
			</div> */}

			<section className=" workspace-toolbar">

				<h1>{currentTitle}</h1>

				<div className="workspace-toolbar-actions">
					<button
						className="ghost-button"
						type="button"
						onClick={() => void refreshPlaylists(selectedId ?? undefined)}
					>
						Refresh
					</button>
					{initialSection === "dashboard" ? (
						<form
							className="workspace-create-inline"
							onSubmit={(event) => {
								event.preventDefault();
								void withBusy("create-playlist", async () => {
									const created = await createPlaylist(createForm);
									setCreateForm({ title: "", description: "" });
									setMessage(`Created playlist "${created.title}".`);
									await refreshPlaylists(created.id);
								});
							}}
						>
							<input
								required

								value={createForm.title}
								onChange={(event) =>
									setCreateForm((current) => ({ ...current, title: event.target.value }))
								}
								placeholder="New playlist title"
								style={{
									background: "#ffffff",
									color: "#8d8f9a;",
									opacity: "80%",
									border: "1px black #8d9a92",
									borderRadius: "16px"
								}}

							/>
							<input

								value={createForm.description}
								onChange={(event) =>
									setCreateForm((current) => ({
										...current,
										description: event.target.value,
									}))
								}
								placeholder="Description"
								style={{
									background: "#ffffff",
									color: "#8d8f9a;",
									opacity: "80%",
									border: "1px black #8d8f9a",
									borderRadius: "16px"
								}}

							/>
							<button className="ghost-button primary-button" disabled={busyAction !== null} type="submit"

							>
								Create
							</button>
						</form>
					) : null}
				</div>
			</section>

			<div className=" workspace-content-grid">
				<aside className="flexColumnLeft workspace-sidebar">
					<div className="workspace-sidebar-header">
						<h2>
							{initialSection === "import" && importSource === "spotify"
								? "Spotify playlists"
								: "Playlists"}
						</h2>
						<span>
							{initialSection === "import" && importSource === "spotify"
								? spotifyPlaylists.length
								: playlists.length}
						</span>
					</div>

					<div className=" flexColumnLeft workspace-list" style={{ marginLeft: "-1.2vw" }}>
						{initialSection === "import" && importSource === "spotify" ? (
							!spotifyToken ? (
								<div className="empty-state" style={{ marginLeft: "-1	.2vw" }}>Connect Spotify to view your playlists.</div>
							) : spotifyPlaylists.length === 0 ? (
								<div className="empty-state" >No Spotify playlists loaded yet.</div>
							) : (
								spotifyPlaylists.map((playlist) => (
									<button
										key={playlist.id}
										className={
											spotifyPlaylistId === playlist.id
												? "workspace-list-row active"
												: "workspace-list-row"
										}
										type="button"
										onClick={() => setSpotifyPlaylistId(playlist.id)}
									>
										{/* <div className="workspace-list-art" aria-hidden="true">
											{playlist.name.slice(0, 1).toUpperCase()}
										</div> */}
										<div className="workspace-list-copy">
											<strong>{playlist.name}</strong>
											<small>
												{playlist.tracks_count > 0
													? `${playlist.tracks_count} tracks`
													: "Spotify playlist"}
											</small>
										</div>
									</button>
								))
							)
						) : playlists.length === 0 ? (
							<div className=" empty-state" style={{ marginLeft: "-1.2vw" }}>No playlists yet.</div>
						) : (
							playlists.map((playlist) => (
								<button
									key={playlist.id}
									className={selectedId === playlist.id ? "workspace-list-row active" : "workspace-list-row"}
									type="button"
									onClick={() => setSelectedId(playlist.id)}
								>
									{/* <div className="workspace-list-art" aria-hidden="true">
										{playlist.title.slice(0, 1).toUpperCase()}
									</div> */}
									<div className="workspace-list-copy">
										<strong>{playlist.title}</strong>
										<small>Playlist</small>
									</div>
								</button>
							))
						)}
					</div>
				</aside>

				<div className="workspace-main">
					{initialSection === "import" ? (
						<section className="workspace-strip stack">
							<div className="section-heading">
								<h2>Import source</h2>
							</div>
							<div className="segmented-control wide" role="tablist" aria-label="Import source">
								<button
									className={importSource === "spotify" ? "segment active" : "segment"}
									type="button"
									onClick={() => setImportSource("spotify")}
								>
									Spotify playlists
								</button>
								<button
									className={importSource === "csv" ? "segment active" : "segment"}
									type="button"
									onClick={() => {
										setImportSource("csv");
										setImportFormat("csv");
									}}
								>
									CSV
								</button>
								<button
									className={importSource === "json" ? "segment active" : "segment"}
									type="button"
									onClick={() => {
										setImportSource("json");
										setImportFormat("json");
									}}
								>
									JSON
								</button>
							</div>
							<div className="section-heading">
								<h2>Import destination</h2>
							</div>
							<div className="segmented-control" role="tablist" aria-label="Import target">
								<button
									className={importPlaylistMode === "new" ? "segment active" : "segment"}
									type="button"
									onClick={() => setImportPlaylistMode("new")}
								>
									New playlist
								</button>
								<button
									className={importPlaylistMode === "existing" ? "segment active" : "segment"}
									type="button"
									onClick={() => setImportPlaylistMode("existing")}
								>
									Existing playlist
								</button>
							</div>

							{importPlaylistMode === "new" ? (
								<div className="field-grid two-columns">
									<label className="field">
										<span>Playlist title</span>
										<input
											value={importCreateForm.title}
											onChange={(event) =>
												setImportCreateForm((current) => ({
													...current,
													title: event.target.value,
												}))
											}
											placeholder="Imported playlist"
										/>
									</label>
									<label className="field">
										<span>Description</span>
										<input
											value={importCreateForm.description}
											onChange={(event) =>
												setImportCreateForm((current) => ({
													...current,
													description: event.target.value,
												}))
											}
											placeholder="Optional description"
										/>
									</label>
								</div>
							) : (
								<label className="field">
									<span>Select playlist</span>
									<select
										value={importTargetId ?? ""}
										onChange={(event) => setImportTargetId(Number(event.target.value) || null)}
									>
										<option value="">Choose a playlist</option>
										{playlists.map((playlist) => (
											<option key={playlist.id} value={playlist.id}>
												{playlist.title}
											</option>
										))}
									</select>
								</label>
							)}

							{importSource === "spotify" ? (
								spotifyToken ? (
									<div className="stack">
										<div className="workspace-inline-actions">
											<button
												className="ghost-button"
												type="button"
												onClick={() => void withBusy("spotify-list", loadSpotifyPlaylists)}
											>
												Refresh Spotify playlists
											</button>
											<button
												className="primary-button"
												disabled={busyAction !== null || !spotifyPlaylistId}
												type="button"
												onClick={() => void withBusy("spotify-import", handleSpotifyImport)}
											>
												Import selected playlist
											</button>
										</div>
									</div>
								) : (
									<div className="muted-panel stack ">
										<p className="muted-copy" style={{ marginLeft: "-1.2vw" }}>
											Connect Spotify to see your personal playlists and choose one to import.
										</p>
										<div className="workspace-inline-actions">
											<button
												className="secondary-button ghost-button"
												type="button"
												onClick={connectSpotifyForImport}
												style={{ color: "black", marginLeft: "-1.2vw" }}
											>
												Connect Spotify
											</button>
										</div>
									</div>
								)
							) : (
								<form
									className="stack"
									onSubmit={(event) => {
										event.preventDefault();
										void withBusy("raw-import", importRawText);
									}}
								>
									<label className="field">
										<span>{importSource.toUpperCase()} playlist data</span>
										<textarea
											className="raw-data-input"
											value={importText}
											onChange={(event) => setImportText(event.target.value)}
											placeholder={
												importFormat === "json"
													? '[{"title":"Track name","artist":"Artist"}]'
													: "title,artist\nTrack name,Artist"
											}
										/>
									</label>
									<div className="muted-panel stack raw-import-options" style={{ marginLeft: "-1.2vw" }}>
										<div className="section-heading">
											<h2>Enrichment options</h2>
										</div>
										<label className="checkbox-row">
											<input
												checked={useSpotifyEnrichmentForRawImport}
												type="checkbox"
												onChange={(event) =>
													setUseSpotifyEnrichmentForRawImport(event.target.checked)
												}
											/>
											<span>
												Use Spotify to resolve tracks and enrich BPM/audio features during and
												after import.
											</span>
										</label>
										<p className="muted-copy">
											{useSpotifyEnrichmentForRawImport
												? session?.spotifyToken
													? "Spotify is connected. We&apos;ll use it to improve organization quality for this imported playlist."
													: "Connect Spotify first to use Spotify-backed enrichment on raw imports."
												: "Import without Spotify if you simply want a fast, raw ingest."}
										</p>
										{useSpotifyEnrichmentForRawImport && !session?.spotifyToken ? (
											<div className="workspace-inline-actions">
												<button
													className="secondary-button ghost-button"
													type="button"
													onClick={connectSpotifyForImport}
												>
													Connect Spotify for enrichment
												</button>
											</div>
										) : null}
									</div>
									<div className="workspace-inline-actions flexRow" style={{ marginTop: "-5vh" }}>
										<button className="primary-button ghost-button" disabled={busyAction !== null} type="submit">
											Import {importSource.toUpperCase()}
										</button>
										<label className="upload-card compact-upload ">
											<span className=" ghost-button">Upload {importSource.toUpperCase()}</span>
											<input
												accept={
													importSource === "csv"
														? ".csv,text/csv"
														: ".json,application/json"
												}
												type="file"
												onChange={(event) => {
													const file = event.target.files?.[0];
													if (!file) {
														return;
													}
													void withBusy(`${importSource}-import`, async () => {
														await importUploadedFile(file, importFormat);
														event.target.value = "";
													});
												}}
											/>
										</label>
									</div>
								</form>
							)}
						</section>
					) : null}

					{initialSection === "import" && importSource === "spotify" && spotifyPlaylistId ? (
						<section className="workspace-strip stack">
							<div className="workspace-playlist-head">
								{/* <div className="workspace-playlist-art large" aria-hidden="true">
									{(selectedSpotifyPlaylist?.name || "S").slice(0, 1).toUpperCase()}
								</div> */}
								<div className="workspace-playlist-meta">
									{/* <div className="eyebrow">Selected playlist</div> */}
									<h2>
										{selectedSpotifyPlaylist?.name || "Selected Spotify playlist"}
									</h2>
									<p className="muted-copy">
										Preview the songs below, then import this playlist into Mixxer.
									</p>
									<div className="workspace-meta-inline">
										<span>{selectedSpotifyTrackCount} tracks</span>
										<span>{spotifyPlaylistTracks.length} in preview</span>
									</div>
								</div>
							</div>

							<div className="workspace-track-layout single">
								<div className="workspace-track-column">
									<div className="section-heading">
										<h3>Track preview</h3>
									</div>
									{spotifyPlaylistTracks.length === 0 ? (
										<div className="empty-state">No Spotify tracks loaded for this playlist yet.</div>
									) : (
										<div className="workspace-track-list">
											{spotifyPlaylistTracks.map((track, index) => (
												<div
													key={`${track.spotify_id ?? track.title ?? index}-${index}`}
													className="workspace-track-row"
												>
													<div className="workspace-track-index">{index + 1}</div>
													<div className="workspace-track-copy">
														<strong>{track.title ?? "Untitled track"}</strong>
														<small>{track.artist || track.album || "Spotify track"}</small>
													</div>
												</div>
											))}
										</div>
									)}
								</div>
							</div>
						</section>
					) : selectedPlaylist ? (
						<section className="workspace-strip stack ">
							<div className="workspace-playlist-head ">
								{/* <div className="workspace-playlist-art large" aria-hidden="true">
									{selectedPlaylist.title.slice(0, 1).toUpperCase()}
								</div> */}
								<div className="workspace-playlist-meta">
									{/* <div className="eyebrow">Selected playlist</div> */}
									<h2>{selectedPlaylist.title}</h2>
									<p className="muted-copy">
										{selectedPlaylist.description || "No description yet."}
									</p>
									<div className="workspace-meta-inline">
										<span>{selectedPlaylist.items.length} tracks</span>

									</div>
								</div>
							</div>

							{selectedPlaylist.enrichment?.pending_tracks ? (
								<div className="muted-panel enrichment-panel">
									<strong>Enrichment in progress</strong>
									<p className="muted-copy">
										{selectedPlaylist.enrichment.enriched_tracks} of{" "}
										{selectedPlaylist.enrichment.enrichable_tracks} Spotify tracks have BPM/audio
										features so far. We&apos;re still filling the rest in automatically.
									</p>
								</div>
							) : selectedPlaylist.enrichment?.enrichable_tracks ? (
								<div className="muted-panel enrichment-panel complete">
									<strong>Enrichment complete</strong>
									<p className="muted-copy">
										Audio features are ready for all {selectedPlaylist.enrichment.enriched_tracks}{" "}
										enrichable tracks in this playlist.
									</p>
								</div>
							) : null}

							{initialSection === "dashboard" ? (
								<form
									className="dashboard-manage-card stack"
									onSubmit={(event) => {
										event.preventDefault();
										void withBusy("update-playlist", handlePlaylistUpdate);
									}}
								>
									<div className="section-heading">
										<h2>Manage playlist</h2>
									</div>
									<div className="field-grid two-columns">
										<label className="field">
											<span>Playlist title</span>
											<input
												value={editForm.title}
												onChange={(event) =>
													setEditForm((current) => ({
														...current,
														title: event.target.value,
													}))
												}
												placeholder="Playlist title"
											/>
										</label>
										<label className="field">
											<span>Description</span>
											<input
												value={editForm.description}
												onChange={(event) =>
													setEditForm((current) => ({
														...current,
														description: event.target.value,
													}))
												}
												placeholder="Optional description"
											/>
										</label>
									</div>
									<div className="workspace-inline-actions workspace-playlist-head">
										<button
											className="ghost-button"
											disabled={busyAction !== null}
											type="submit"
										>
											Save changes
										</button>
										<button
											className="danger-button "
											disabled={busyAction !== null}
											type="button"
											onClick={() => {
												const shouldDelete = window.confirm(
													`Delete "${selectedPlaylist.title}"? This cannot be undone.`,
												);
												if (!shouldDelete) {
													return;
												}
												void withBusy("delete-playlist", handlePlaylistDelete);
											}}
										>
											Delete playlist
										</button>
									</div>
								</form>
							) : null}

							{initialSection !== "dashboard" ? (
								<form
									className="workspace-action-row"
									onSubmit={(event) => {
										event.preventDefault();
										void withBusy("organize", async () => {
											const result = await organizePlaylist(selectedPlaylist.id, organizeMode);
											setOrganizedTracks(result);
											setMessage(`Organized playlist using ${organizeMode}.`);
										});
									}}
								>
									<label className="field">
										<span>Organization mode</span>
										<select
											value={organizeMode}
											onChange={(event) => setOrganizeMode(event.target.value)}
										>
											<option value="smart_mix">Smart mix</option>
											<option value="bpm">BPM</option>
											<option value="energy">Energy</option>
											<option value="valence">Mood</option>
										</select>
									</label>
									<button className="secondary-button ghost-button" disabled={busyAction !== null} type="submit" style={{ color: "black", marginLeft: ".5vw" }}>
										Preview playlist
									</button>
									{initialSection === "export" ? (
										<>
											<label className="field">
												<span>Export name</span>
												<input
													value={exportName}
													onChange={(event) => setExportName(event.target.value)}
													placeholder={selectedPlaylist.title}
												/>
											</label>
											{session?.spotifyToken ? (
												<button
													className="primary-button"
													disabled={busyAction !== null}
													type="button"
													onClick={() =>
														void withBusy("export", async () => {
															const result = await exportPlaylist(
																selectedPlaylist.id,
																exportName || undefined,
															);
															const tracksAdded = result.tracks_added ?? 0;
															const duplicatesSkipped = result.duplicates_skipped ?? 0;
															const missingSpotifyIds =
																result.tracks_skipped_without_spotify_id ?? 0;
															const exportParts = [
																`Spotify export created playlist ${result.spotify_playlist_id}`,
																`${tracksAdded} track${tracksAdded === 1 ? "" : "s"} added`,
															];

															if (duplicatesSkipped > 0) {
																exportParts.push(
																	`${duplicatesSkipped} duplicate${duplicatesSkipped === 1 ? "" : "s"} skipped`,
																);
															}

															if (missingSpotifyIds > 0) {
																exportParts.push(
																	`${missingSpotifyIds} track${missingSpotifyIds === 1 ? "" : "s"} without Spotify IDs skipped`,
																);
															}

															setMessage(`${exportParts.join(", ")}.`);
														})
													}
												>
													Export to Spotify
												</button>
											) : (
												<button
													className="secondary-button ghost-button"
													disabled={busyAction !== null}
													type="button"
													onClick={connectSpotifyForExport}
												>
													Connect Spotify to export
												</button>
											)}
										</>
									) : null}
								</form>
							) : null}

							{initialSection === "export" ? (
								<div className="muted-panel export-status-panel" style={{marginLeft: "-1vw"}}>
									<strong>
										{session?.spotifyToken ? "Spotify export is ready" : "Spotify connection required"}
									</strong>
									<p className="muted-copy">
										{session?.spotifyToken
											? "We'll create a Spotify playlist from the tracks in this MusicMixxer playlist. Tracks without Spotify IDs are skipped automatically."
											: "Connect Spotify first to export this playlist. Your MusicMixxer playlist will stay here either way."}
									</p>
								</div>
							) : null}

							<div className="workspace-track-layout">
								<div className="workspace-track-column ">
									<div className=" section-heading ">
										<h2>Tracks</h2>

									</div>
									{selectedPlaylist.items.length === 0 ? (
										<div className="empty-state" style={{ marginLeft: "-1.2vw" }}>This playlist has no imported tracks yet.</div>
									) : (
										<div className="workspace-track-list">
											{selectedPlaylist.items.map((item) => (
												<div key={item.id} className="workspace-track-row">
													<div className="workspace-track-index">{item.position}</div>
													<div className="workspace-track-copy">
														<strong>{item.track?.title ?? "Untitled track"}</strong>
														<small>{formatMetric(item.track?.bpm, "BPM")}</small>
													</div>
												</div>
											))}
										</div>
									)}
								</div>

								{/* {initialSection !== "dashboard" ? ( */}
								<div className="workspace-track-column">
									{/* <div className="section-heading">
											<h3>Organized preview</h3>
										</div>
										{organizedTracks.length === 0 ? (
											<div className="empty-state">
												Run an organization mode to preview the backend ordering.
											</div>
										) : ( */}
									<div className="workspace-track-list">
										{organizedTracks.map((track, index) => (
											<div key={`${track.id}-${index}`} className="workspace-track-row accent">
												<div className="workspace-track-index">{index + 1}</div>
												<div className="workspace-track-copy">
													<strong>{track.title}</strong>
													<small>{formatMetric(track.bpm, "BPM")}</small>
												</div>
											</div>
										))}
									</div>
									{/* )} */}
								</div>
								{/* ) : null} */}
							</div>
						</section>
					) : (
						<section className="workspace-stri flexColumn ">
							{/* <div className="empty-state  ">
								{initialSection === "import" && importSource === "spotify"
									? "Select one of your Spotify playlists from the left to inspect its tracks."
									: initialSection === "dashboard"
									? "Select a playlist from the left to browse it."
									: initialSection === "import"
										? "Import raw playlist data and it will appear here."
										: "Select a playlist to prepare it for export."}
							</div> */}
						</section>
					)}
				</div>
			</div>
		</div>
	);
}

function formatMetric(value: number | null | undefined, label: string) {
	if (value === null || value === undefined) {
		return `No ${label}`;
	}
	return `${Math.round(value)} ${label}`;
}
