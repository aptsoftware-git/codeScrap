# Frontend Cancel Issue - Session ID Not Available

## Problem Diagnosis

**Symptom**: When clicking Cancel button, no `[CANCEL-REQUEST]` logs appear in the backend.

**Root Cause**: The cancel request is NOT being sent to the backend at all.

**Why**: The `streamService.currentSessionId` is `null` when cancel is clicked.

---

## Why Session ID is Null

The session ID is set when the `session` event is received from the backend SSE stream:

```typescript
// Session event handler
this.eventSource.addEventListener('session', (event) => {
  const data = JSON.parse(event.data);
  this.currentSessionId = data.session_id;  // ← Session ID stored here
});
```

### **Timing Issue**:

If you click Cancel **immediately after clicking Search** (within ~100-500ms), the sequence is:

1. User clicks "Search" button
2. Frontend calls `streamService.startStreaming()`
3. Frontend opens SSE connection to backend
4. **User clicks "Cancel" button** ← TOO FAST!
5. Frontend tries to call `streamService.cancel()`
6. But `currentSessionId` is still `null` because the backend hasn't sent the session event yet
7. Cancel function exits early: `if (!this.currentSessionId) { return; }`
8. No cancel request is sent to backend
9. Backend continues processing

---

## Solution

The cancel method needs to close the connection **even if session ID is null**.

### Fixed Code:

```typescript
async cancel(): Promise<void> {
  console.log('[CANCEL] Cancel called, currentSessionId:', this.currentSessionId);
  
  if (!this.currentSessionId) {
    console.warn('[CANCEL] No active session to cancel - session ID is null/undefined');
    console.warn('[CANCEL] This likely means the session event has not been received yet');
    // ✅ STILL close the connection to stop the stream
    this.close();
    return;
  }

  const sessionId = this.currentSessionId;
  console.log(`[CANCEL] Sending cancel request for session: ${sessionId}`);

  try {
    const url = `${this.baseURL}/api/v1/search/cancel/${sessionId}`;
    console.log(`[CANCEL] POST to ${url}`);
    
    const response = await fetch(url, {
      method: 'POST',
    });

    console.log(`[CANCEL] Response status: ${response.status}`);

    if (!response.ok) {
      throw new Error(`Cancel request failed: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('[CANCEL] Cancellation response:', result);
    
    this.close();
  } catch (error) {
    console.error('[CANCEL] Error cancelling search:', error);
    this.close(); // ✅ Close connection even if cancel request fails
    throw error;
  }
}
```

---

## Test Instructions

### **Open Browser Console** (F12)

1. Click "Search" button
2. **Immediately** click "Cancel" button (within 1 second)
3. Look at console logs

### **Expected Logs - Before Fix**:

```
[STREAM] Opening SSE connection: http://...
[CANCEL] Cancel called, currentSessionId: null
[CANCEL] No active session to cancel - session ID is null/undefined
[CANCEL] This likely means the session event has not been received yet
❌ Connection NOT closed - backend keeps streaming!
[SESSION] Session started, ID: abc123  ← Arrives AFTER cancel
```

### **Expected Logs - After Fix**:

```
[STREAM] Opening SSE connection: http://...
[CANCEL] Cancel called, currentSessionId: null
[CANCEL] No active session to cancel - session ID is null/undefined
[CANCEL] This likely means the session event has not been received yet
[CLOSE] Closing SSE connection  ← ✅ Connection closed!
✅ No more logs - connection stopped
```

---

## Additional Logging Added

All frontend logs now have `[TAG]` prefixes for easy filtering:

- `[STREAM]` - SSE connection opened
- `[SESSION]` - Session ID received
- `[PROGRESS]` - Progress updates
- `[EVENT]` - New event extracted
- `[COMPLETE]` - Search completed
- `[CANCELLED]` - Search cancelled
- `[ERROR]` - Errors
- `[CANCEL]` - Cancel operations
- `[CLOSE]` - Connection closed

---

## Backend Logging

The backend also has detailed logging:

- `[CANCEL-REQUEST]` - Cancel endpoint called
- `[SESSION-STORE]` - Session marked as cancelled
- `[CANCEL-CHECK]` - Cancellation checks
- `[CANCELLED]` - Cancellation detected
- `[SCRAPING]` - Web scraping operations
- `[LLM]` - LLM processing

---

## Next Steps

1. **Test in browser console** - You should now see `[CANCEL]` logs
2. **If session ID is null** - Connection will close (stops backend streaming)
3. **If session ID exists** - Cancel request will be sent to backend
4. **Check backend logs** - Should see `[CANCEL-REQUEST]` when session ID exists

---

## Why This Happens

The backend sends the session ID as the **first SSE event**:

```python
# Backend sends this first
yield f"data: {json.dumps({'event_type': 'session', 'session_id': session_id})}\n\n"
```

But there's a small delay:
1. HTTP connection setup (~50-100ms)
2. Backend creates session (~10ms)
3. Backend sends session event (~10ms)
4. Network transmission (~10-50ms)
5. Frontend receives event (~10ms)

**Total delay**: ~100-200ms before session ID is available

If user clicks Cancel within this window, session ID is still null!

---

## Status

✅ **Fixed** - `streamService.ts` now closes connection even if session ID is null
✅ **Logging added** - Both frontend and backend have detailed logs
🧪 **Ready to test** - Open browser console and try immediate cancel

The frontend should auto-reload. Try clicking Cancel immediately after Search and check the browser console!
