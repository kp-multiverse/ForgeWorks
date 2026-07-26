//! Application core logic.

/// Returns a friendly greeting for `name`.
///
/// Placeholder so the scaffold passes the quality gate from the first run.
/// Delete it (and its tests) when you build your first slice; real code
/// follows the conventions in `docs/language-standards.md` (one concept per
/// file, ~100-line target, 200-line hard cap).
pub fn greet(name: &str) -> String {
    format!("Hello, {name}!")
}

#[cfg(test)]
mod tests {
    use super::greet;

    #[test]
    fn greet_returns_greeting() {
        assert_eq!(greet("world"), "Hello, world!");
    }
}
