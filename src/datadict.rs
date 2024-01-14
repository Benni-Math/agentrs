use rustc_hash::FxHashMap;

// TODO: run_id, reporters, optimization of agent_props
pub struct DataDict<'a> {
    pub agent_props: Vec<Vec<FxHashMap<&'a str, i64>>>,
}

// TODO: integration with PolaRS
impl DataDict<'_> {
    pub fn new() -> Self {
        Self {
            agent_props: Vec::new(),
        }
    }
}
