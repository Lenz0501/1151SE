<?php

/**
 * Fix IME composition conflicts in Adminer's official Jush SQL editor.
 *
 * This plugin does not replace the editor or autocomplete implementation.
 * It pauses Jush input and keyboard handlers during IME composition, then
 * synchronizes the committed text and optionally reopens official completion.
 *
 * @link https://www.adminer.org/plugins/#use
 */
class AdminerImeAutocomplete extends Adminer\Plugin
{
    /** @var bool */
    private $reopenAutocomplete;

    /**
     * @param bool $reopenAutocomplete Reopen Adminer's suggestions after IME commit.
     */
    public function __construct($reopenAutocomplete = true)
    {
        $this->reopenAutocomplete = $reopenAutocomplete;
    }

    public function syntaxHighlighting($tableStatuses)
    {
        ?>
<script <?php echo Adminer\nonce(); ?>>
addEventListener('DOMContentLoaded', () => {
    // Adminer's own DOMContentLoaded handler is registered after this plugin.
    // Defer once so the official contenteditable Jush editor already exists.
    setTimeout(() => {
        const composing = new WeakSet();
        const pendingCommit = new WeakSet();
        const reopenAutocomplete = <?php echo $this->reopenAutocomplete ? 'true' : 'false'; ?>;

        function editorFromEvent(event) {
            const target = event.target;
            return target instanceof Element
                && target.matches('pre.jush[contenteditable="true"]')
                ? target
                : null;
        }

        function closeAutocomplete() {
            for (const popup of document.querySelectorAll('.jush-autocomplete')) {
                popup.style.display = 'none';
            }
        }

        // Capture before Jush's target listeners. Do not preventDefault(): the
        // browser/IME must remain free to update the contenteditable element.
        document.addEventListener('keydown', event => {
            const editor = editorFromEvent(event);
            if (
                editor
                && (composing.has(editor) || event.isComposing || event.keyCode === 229)
            ) {
                closeAutocomplete();
                event.stopImmediatePropagation();
            }
        }, true);

        document.addEventListener('input', event => {
            const editor = editorFromEvent(event);
            if (editor && composing.has(editor)) {
                // Jush normally rebuilds the contenteditable DOM on input.
                // Doing that mid-composition cancels or corrupts some IMEs.
                pendingCommit.add(editor);
                closeAutocomplete();
                event.stopImmediatePropagation();
            }
        }, true);

        document.addEventListener('compositionstart', event => {
            const editor = editorFromEvent(event);
            if (!editor) return;
            composing.add(editor);
            pendingCommit.add(editor);
            closeAutocomplete();
        }, true);

        document.addEventListener('compositionupdate', event => {
            if (editorFromEvent(event)) closeAutocomplete();
        }, true);

        document.addEventListener('compositionend', event => {
            const editor = editorFromEvent(event);
            if (!editor) return;

            composing.delete(editor);

            // Let the browser finish committing the composed text first.
            setTimeout(() => {
                if (pendingCommit.has(editor)) {
                    pendingCommit.delete(editor);
                    editor.oninput();
                }

                if (reopenAutocomplete) {
                    // editor.oninput() defers Jush highlighting once more. Open
                    // completion only after that rebuild has restored selection.
                    setTimeout(() => {
                        if (!composing.has(editor) && document.activeElement === editor) {
                            editor.dispatchEvent(new KeyboardEvent('keydown', {
                                key: ' ',
                                code: 'Space',
                                ctrlKey: true,
                                bubbles: false,
                                cancelable: true
                            }));
                        }
                    }, 0);
                }
            }, 0);
        }, true);

        // Some browsers report the final input after compositionend. If Jush
        // already handled it, the scheduled sync sees no changed DOM and is safe.
        document.addEventListener('blur', event => {
            const editor = editorFromEvent(event);
            if (!editor) return;
            composing.delete(editor);
            pendingCommit.delete(editor);
            closeAutocomplete();
        }, true);
    }, 0);
});
</script>
<?php
        // Deliberately return null. Adminer's official syntaxHighlighting()
        // continues afterward and creates the normal Jush editor/autocomplete.
    }
}
